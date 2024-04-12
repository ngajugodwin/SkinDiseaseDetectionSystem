class Config:
    #Session time out
    PERMANENT_SESSION_LIFETIME = 24 * 60 * 60
    #Application secret key
    SECRET_KEY = 'secret key'
    #Image uploads directory
    UPLOAD_FOLDER = 'static/uploads'
    #Allowed file formats for image upload
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    #Max upload file size
    MAX_UPLOAD_FILE_SIZE = 2 * 1024 * 1024
    # Database configuration
    DB_NAME = 'skindiseases_db'
    DB_USER = 'postgres'
    DB_PASSWORD = 'DB_PASSWORD'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    #Flask-Mail Configuration
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '7f5e2713904294'
    MAIL_PASSWORD = 'MAILTRAP_PASSWORD'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    #Mail config
    MAIL_TITLE = 'Report from Skin Diseases'
    MAIL_SENDER_EMAIL = 'info@skindiseases.com'