from keras.preprocessing.image import load_img, img_to_array
import numpy as np
from keras.models import load_model
from config.config import Config


class Helpers:

    model = load_model('Skin_Diseases_Model_New.h5')

    def prepare_image(self, img_path):
        img = load_img(img_path, target_size=(224, 224, 3))
        img = img_to_array(img)
        img = img / 255
        img = np.expand_dims(img, [0])
        answer = self.model.predict(img)
        y_class = answer.argmax(axis=-1)
        y = " ".join(str(x) for x in y_class)
        return int(y)

    def allowed_image_format(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS