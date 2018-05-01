import csv
import os
import os.path

import numpy as np
import cv2


class SimpleDatasetLoader:
    def __init__(self, preprocessors=None):
        if preprocessors is None:
            preprocessors = []

        self.preprocessors = preprocessors

    def load(self, driving_log_path, data_path, verbose=False):
        logs = []
        with open(driving_log_path, 'r') as f:
            reader = csv.DictReader(f)
            logs = reader.readlines()

        data = []
        labels = []
        # if verbose, we will print 10 info messages
        verbose_period = len(logs) // 10

        delta = 0.08
        # load center camera image
        for i, log in enumerate(logs):
            center_image_path = os.path.join(data_path, log['center'])
            center_image = cv2.imread(center_image_path)
            for p in self.preprocessors:
                center_image = p.preprocess(center_image)
            data.append(center_image)
            labels.append(float(logs['steering']))

            left_image_path = os.path.join(data_path, log['left'])
            left_image = cv2.imread(left_image_path)
            for p in self.preprocessors:
                left_image = p.preprocess(left_image)
            data.append(left_image)
            labels.append(float(logs['steering'] + delta))

            right_image_path = os.path.join(data_path, log['right'])
            right_image = cv2.imread(right_image_path)
            for p in self.preprocessors:
                right_image = p.preprocess(right_image)
            data.append(right_image)
            labels.append(float(logs['steering'] - delta))

            if verbose and (i % verbose_period == 0):
                print(f'[INFO] processed {i + 1}/{len(logs)}')

        return np.array(data), np.array(labels)
