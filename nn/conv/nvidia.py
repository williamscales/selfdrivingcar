from keras.models import Sequential
from keras.layers.convolutional import Conv2D
from keras.layers.core import (
    Activation,
    Dense,
    Dropout,
    Flatten,
    Lambda,
)
from keras.layers.pooling import MaxPooling2D
from keras import backend as K


class NvidiaNet:
    @staticmethod
    def build(width, height, depth, classes):
        model = Sequential()
        input_shape = (height, width, depth)

        if K.image_data_format() == 'channels_first':
            input_shape = (depth, height, width)

        model.add(Lambda(lambda x: x / 127.5 - 1, input_shape=input_shape))

        model.add(Conv2D(8, 3, 3, init='normal', border_mode='valid'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D((2, 2), border_mode='valid'))

        model.add(Conv2D(8, 3, 3, init='normal', border_mode='valid'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D((2, 2), border_mode='valid'))

        model.add(Dropout(0.2))
        model.add(Flatten())
        model.add(Dense(50))
        model.add(Activation('relu'))
        model.add(Dense(1))
        return model
