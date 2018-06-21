import argparse
import sys

from imutils import paths
from keras.optimizers import SGD, Adam
from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils import shuffle

from preprocessing import (
    ImageToArrayPreprocessor,
    SimplePreprocessor,
)
from datasets import SimpleDatasetLoader
from nn.conv import (
    MiniVGGNet,
    NvidiaNet,
    ShallowNet,
    TinyNet,
)

img_rows = 20
img_cols = 32
# img_rows = 240
# img_cols = 320

learning_rate = 0.02
batch_size = 32
nb_epoch = 50


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
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
    parser.add_argument(
        '-m',
        '--model',
        required=True,
        help='path to output model',
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
        driving_log_path=options.driving_log,
        data_path=options.dataset,
        verbose=True,
    )
    data = data.astype('float32')
    import ipdb; ipdb.set_trace()

    # # horizontal reflection for augmentation
    # data = np.append(data, data[:, :, ::-1], axis=0)
    # labels = np.append(labels, -labels, axis=0)

    # split train and validation
    data, labels = shuffle(data, labels)
    x_train, x_test, y_train, y_test = train_test_split(
        data,
        labels,
        random_state=13,
        test_size=0.1,
    )
    # x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
    # x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)

    lb = LabelBinarizer()
    y_train = lb.fit_transform(y_train)
    y_test = lb.transform(y_test)

    label_names = ['straight', 'left', 'right']

    aug = ImageDataGenerator(
        rotation_range=1,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.2,
        horizontal_flip=False,
        fill_mode="nearest",
    )

    print('[INFO] compiling model...')
    # model = NvidiaNet.build(width=img_cols, height=img_rows, depth=1)
    # model = TinyNet.build(width=img_cols, height=img_rows, depth=1)
    # model = ShallowNet.build(width=img_cols, height=img_rows, depth=1, classes=len(label_names))
    model = MiniVGGNet.build(width=img_cols, height=img_rows, depth=1, classes=len(label_names))

    opt = SGD(lr=learning_rate, momentum=0.9, decay=learning_rate/nb_epoch, nesterov=True)
    # opt = SGD(lr=learning_rate)
    # opt = Adam(lr=learning_rate)
    # model.compile(
    #     loss='mean_squared_error',
    #     metrics=["accuracy"],
    #     optimizer=opt,
    # )
    model.compile(
        loss='categorical_crossentropy',
        metrics=['accuracy'],
        optimizer=opt,
    )

    history = model.fit_generator(
        aug.flow(x_train, y_train, batch_size=batch_size),
    # history = model.fit(
    #     x_train, y_train,
        nb_epoch=nb_epoch,
        # batch_size=batch_size,
        steps_per_epoch=(len(x_train) // batch_size),
        verbose=1,
        validation_data=(x_test, y_test),
    )

    predictions = model.predict(x_test, batch_size=batch_size)
    print(classification_report(
        y_test.argmax(axis=1),
        predictions.argmax(axis=1),
        target_names=label_names,
    ))

    plt.style.use("ggplot")
    fig, ax_acc = plt.subplots(1, 1)

    ax_acc.set_xlabel("Epoch #")

    ax_loss = ax_acc.twinx()
    ax_loss.grid(None)
    ax_loss.set_ylabel("Loss")

    ax_acc.grid(None)
    ax_acc.set_ylabel("Accuracy")
    ax_acc.set_ylim([0, 1])

    ax_loss.plot(np.arange(0, nb_epoch), history.history["loss"], label="train_loss")
    ax_loss.plot(np.arange(0, nb_epoch), history.history["val_loss"], label="val_loss")
    ax_acc.plot(np.arange(0, nb_epoch), history.history["acc"], label="train_acc")
    ax_acc.plot(np.arange(0, nb_epoch), history.history["val_acc"], label="val_acc")
    fig.suptitle("Training Loss and Accuracy")
    fig.legend()
    plt.show()

    model.save(options.model)

    return 0


if __name__ == '__main__':
    sys.exit(main())
