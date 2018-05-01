from keras.preprocessing.image import img_to_array


class ImageToArrayPreProcessor:
    def __init__(self, data_format: bool=True) -> None:
        self.data_format = data_format

    def preprocess(self, image):
        return img_to_array(image, data_format=self.data_format)
