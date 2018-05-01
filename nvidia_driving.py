import argparse
import sys

from imutils import paths
from keras.optimizers import SGD
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils import shuffle

from selfdrivingcar.preprocessing import (
    ImageToArrayPreprocessor,
    SimplePreprocessor,
)
from selfdrivingcar.datasets import SimpleDatasetLoader
from selfdrivingcar.nn.conv import NvidiaNet

img_rows = 16
img_cols = 32

batch_size = 128
nb_epoch = 10


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_pargument(
        '-l',
        '--driving-log',
        required=True,
        help='path to driving log',
    )
    parser.add_argument(
        '-d',
        '--dataset',
        required=True,
        help='path to camera images',
    )
    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    options = parse_args(argv)

    print("[INFO] loading images...")

    loader = SimpleDatasetLoader(preprocessors=[
        SimplePreprocessor(width=img_cols, height=img_rows),
        ImageToArrayPreprocessor(),
    ])
    data, labels = loader.load(
        driving_log=options.driving_log,
        data_path=options.dataset,
        verbose=True,
    )
    data = data.astype('float32')
    labels = labels.astype('float32')

    # horizontal reflection for augmentation
    data = np.append(data, data[:, :, ::-1], axis=0)
    labels = np.append(labels, labels, axis=0)

    # split train and validation
    data, labels = shuffle(data, labels)
    x_train, x_test, y_train, y_test = train_test_split(
        data,
        labels,
        random_state=0,
        test_size=0.1,
    )
    x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)

    print('[INFO] compiling model...')
    model = NvidiaNet.build(width=img_cols, height=img_rows, depth=3)

    model.compile(
        loss='mean_squared_error',
        optimizer='adam',
    )

    history = model.fit(
        x_train,
        y_train,
        batch_size=batch_size,
        nb_epoch=nb_epoch,
        verbose=1,
        validation_data=(x_test, y_test),
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
