import os
from flask import Flask, render_template, request, url_for, session, flash, redirect, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from config.config import Config
from utils.utils import Helpers
from flask_mail import Mail, Message

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

def connect_db():
    conn = psycopg2.connect(database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASSWORD, host=Config.DB_HOST,
                        port=Config.DB_PORT)
    return conn

#Account creation
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        password = request.form.get('password')
        email = request.form.get('email')
        #validate that fullname, password and email are provided
        if not fullname or not password or not email:
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        try:
            conn = connect_db()
            cur = conn.cursor()
            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cur.fetchone()
            if existing_user:
                flash('Email already exists. Please choose a different email.', 'error')
                return redirect(url_for('register'))
            # Create a new user
            cur.execute("INSERT INTO users (fullname, password, email, date_created) VALUES (%s, %s, %s, CURRENT_DATE)", (fullname, hashed_password, email))
            conn.commit()
            cur.close()
            conn.close()
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('register'))
        except Exception as e:
            flash('An error occurred while creating your account.'+ str(e), 'error')
            return redirect(url_for('error'))
    return render_template('register.html')

#Login
@app.route('/')
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['is_logged_in'] = True
            session['id'] = user[0]
            session['name'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error = 'Invalid username or password')
    return render_template('login.html')

#Dashboard
@app.route('/dashboard')
def dashboard():
    if 'is_logged_in' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/send_email', methods = ['POST'])
def send_email():
    receiver_email = request.form.get('receiver_email')
    name = request.form.get('name')
    causes = request.form.get('causes')
    prevention = request.form.get('prevention')
    treatment = request.form.get('treatment')
    # Create a message
    msg = Message(Config.MAIL_TITLE,
                  sender=Config.MAIL_SENDER_EMAIL,
                  recipients=[receiver_email])
    msg.body = f'This summary provides an insight into the skin disorder identified as {name}, according to the system\'s diagnosis. It outlines the potential causes behind {name} as {causes} and suggests measures for its prevention using {prevention}.'

    # Send the message
    mail.send(msg)
    return jsonify({
        "code": 'SUCCESS',
        "message": 'Mail sent successfully',
    }), 200


#Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#Error page
@app.route('/error')
def error():
    return render_template('error.html')

#Image recognition
@app.route('/recognize', methods = ['POST'])
def recognize_disease():
    image = request.files['image']
    if image.filename != '':
        if image and Helpers.allowed_image_format(image.filename) and len(image.read()) < Config.MAX_UPLOAD_FILE_SIZE:
            image.seek(0)
            filename = secure_filename(image.filename)
            save_image_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            image.save(save_image_path)
            helper_instance = Helpers()
            label_index = helper_instance.prepare_image(save_image_path)
            try:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM diseases WHERE label_index = %s", (label_index,))
                data = cur.fetchone()

                # Get logged in user ID
                user_id = session.get('id')

                # Insert into Photogallery table
                cur.execute("INSERT INTO photogallery (photo, userid, skindiseaseid) VALUES (%s, %s, %s)", (filename, user_id, data[0]))
                conn.commit()

                cur.close()
                conn.close()
                return render_template('index.html', data = data, filename = filename)
            except Exception as e:
                flash('An error occurred while creating your account.' + str(e), 'error')
                return redirect(url_for('error'))
        flash("Select an image that has the supported file formats and size", "error")
        return render_template('index.html')
    else:
        flash("An image needs to be selected")
        return render_template('index.html')

@app.route('/history', methods = ['GET'])
def history():
    user_id = session.get('id')
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT d.id, COUNT(*) AS total_photos, d.name FROM photogallery p join diseases d on p.skindiseaseid = d.id where userid = %s group by d.name, d.id", (user_id,))
        data = cur.fetchall()

        cur.close()
        conn.close()
        return render_template('history.html', data=data)
    except Exception as e:
        flash('An error occurred while fetching history.' + str(e), 'error')
        return redirect(url_for('error'))

@app.route('/images/<disease_name>/<int:disease_id>', methods = ['GET'])
def load_images(disease_name, disease_id):
    user_id = session.get('id')
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT photo FROM photogallery where userid = %s and skindiseaseid = %s", (user_id, disease_id))
        data = cur.fetchall()

        cur.close()
        conn.close()
        return render_template('images.html', data=data, name=disease_name)
    except Exception as e:
        flash('An error occurred while loading images.' + str(e), 'error')
        return redirect(url_for('error'))


if __name__ == '__main__':
    app.run(host="0.0.0.0")