import os

import numpy as np
import cv2


class SimpleDatasetLoader:
    def __init__(self, preprocessors=None):
        if preprocessors is None:
            preprocessors = []

        self.preprocessors = preprocessors

    def load(self, image_paths, verbose=False):
        data = []
        labels = []
        # if verbose, we will print 10 info messages
        verbose_period = len(image_paths) // 10

        for i, path in enumerate(image_paths):
            image = cv2.imread(path)
            label = path.split(os.path.sep)[-2]

            for p in self.preprocessors:
                image = p.preprocess(image)

            data.append(image)
            labels.append(label)

            if verbose and (i % verbose_period == 0):
                print(f'[INFO] processed {i + 1}/{len(image_paths)}')

        return np.array(data), np.array(labels)
