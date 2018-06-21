from keras.models import Sequential
from keras.layers.advanced_activations import ELU
from keras.layers.convolutional import Conv2D
from keras.layers.core import (
    Dense,
    Dropout,
    Flatten,
    Lambda,
)
from keras.layers.pooling import MaxPooling2D

from keras import backend as K


class TinyNet:
    @staticmethod
    def build(width, height, depth):
        model = Sequential()
        input_shape = (height, width, depth)

        if K.image_data_format() == 'channels_first':
            input_shape = (depth, height, width)

        model.add(Lambda(lambda x: x / 127.5 - 1, input_shape=input_shape))

        model.add(Conv2D(2, (3, 3), padding='valid', activation='relu'))
        model.add(MaxPooling2D((4, 4), (4, 4), 'valid'))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(1))

        return model
