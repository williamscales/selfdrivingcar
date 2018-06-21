from keras.models import Sequential
from keras.layers.advanced_activations import ELU
from keras.layers.convolutional import Conv2D
from keras.layers.core import (
    Dense,
    Dropout,
    Flatten,
    Lambda,
)

from keras import backend as K


class CommaAiNet:
    @staticmethod
    def build(width, height, depth):
        model = Sequential()
        input_shape = (height, width, depth)

        if K.image_data_format() == 'channels_first':
            input_shape = (depth, height, width)

        model.add(Lambda(lambda x: x / 127.5 - 1, input_shape=input_shape))

        model.add(Conv2D(16, (8, 8), strides=(4, 4), padding="same"))
        model.add(ELU())

        model.add(Conv2D(32, (5, 5), strides=(2, 2), padding="same"))
        model.add(ELU())

        model.add(Conv2D(64, (5, 5), strides=(2, 2), padding="same"))

        model.add(Flatten())
        model.add(Dropout(.2))
        model.add(ELU())
        model.add(Dense(512))
        model.add(Dropout(.5))
        model.add(ELU())
        model.add(Dense(1))
        return model
