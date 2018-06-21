import csv
import os

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
            logs = list(reader)

        data = []
        labels = []
        # if verbose, we will print 10 info messages
        verbose_period = len(logs) // 10

        # delta = 0.08
        # load center camera image
        for i, log in enumerate(logs):
            image_file = os.path.basename(log['frame_filename'])
            center_image_path = os.path.join(data_path, image_file)
            center_image = cv2.imread(center_image_path)
            for p in self.preprocessors:
                center_image = p.preprocess(center_image)
            data.append(center_image)
            data.append(center_image[:, ::-1, :])
            steering = int(log['steering_value'])
            # 0 -> straight, 1 -> left, 2 -> right
            if steering > 92:
                labels.append(2)
                labels.append(1)
            elif steering < 92:
                labels.append(1)
                labels.append(2)
            else:
                labels.append(0)
                labels.append(0)

            # left_image_path = os.path.join(data_path, log['left'])
            # left_image = cv2.imread(left_image_path)
            # for p in self.preprocessors:
            #     left_image = p.preprocess(left_image)
            # data.append(left_image)
            # labels.append(float(logs['steering_value'] + delta))

            # right_image_path = os.path.join(data_path, log['right'])
            # right_image = cv2.imread(right_image_path)
            # for p in self.preprocessors:
            #     right_image = p.preprocess(right_image)
            # data.append(right_image)
            # labels.append(float(logs['steering_value'] - delta))

            if verbose and (i % verbose_period == 0):
                print(f'[INFO] processed {i + 1}/{len(logs)}')

        return np.array(data), np.array(labels)
