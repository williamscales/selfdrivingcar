from argparse import ArgumentParser
import asyncio
import concurrent.futures
import csv
import cv2
import http.client
from io import BytesIO
import logging
import os
import socket
import sys
import time

import numpy as np
from PIL import Image

from nn.conv import MiniVGGNet
from preprocessing import (
    ImageToArrayPreprocessor,
    SimplePreprocessor,
)


def get_frame(ip):
    http_data = http.client.HTTPConnection(ip, 8080)
    http_data.putrequest('GET', '/?action=snapshot')
    http_data.putheader('Host', '10.0.0.9')
    http_data.putheader('User-agent', 'python-http.client')
    http_data.putheader('Content-type', 'image/jpeg')
    http_data.endheaders()
    returnmsg = http_data.getresponse()
    b = returnmsg.read()
    bio = BytesIO(b)
    # return Image.open(bio)
    # return cv2.imread(bio)
    file_bytes = np.asarray(bytearray(bio.read()), dtype=np.uint8)
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-m',
        '--model',
        required=True,
        help='path to model',
    )
    parser.add_argument(
        '-i',
        '--ip',
        required=True,
        help='ip of raspi',
    )
    options = parser.parse_args()

    img_rows = 20
    img_cols = 32
    label_names = ['straight', 'left', 'right']
    preprocessors = [
        ImageToArrayPreprocessor(),
        SimplePreprocessor(width=img_cols, height=img_rows),
    ]

    model = MiniVGGNet.build(width=img_cols, height=img_rows, depth=1, classes=len(label_names))
    model.load_weights(options.model)

    # command_throttle_forward(45)
    while True:
        image = get_frame(options.ip)
        for processor in preprocessors:
            image = processor.preprocess(image)
        data = np.array([image.reshape(20, 32, 1)])
        prediction = model.predict(data, batch_size=1)
        direction = prediction.argmax(axis=1)[0]
        lookup = {
            0: 92,
            1: 70,
            2: 112,
        }
        converted_steering = lookup[direction]
        throttle_dir = 'r'
        converted_throttle = 45
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((options.ip, 9999))
        sock.send(f's {converted_steering} {throttle_dir} {converted_throttle}'.encode())
