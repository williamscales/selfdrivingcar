import cv2


class SimplePreprocessor:
    def __init__(
            self,
            width,
            height,
            color_space=cv2.COLOR_RGB2HSV,
            interpolation=cv2.INTER_AREA,
    ):
        self.width = width
        self.height = height
        self.color_space = color_space
        self.interpolation = interpolation

    def preprocess(self, image):
        return cv2.resize(
            cv2.cvtColor(image, self.color_space)[:, :, 1],
            (self.width, self.height),
            interpolation=self.interpolation,
        )
