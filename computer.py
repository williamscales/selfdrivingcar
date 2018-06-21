from argparse import ArgumentParser
import socket
import sys
from time import sleep

from controller import PS4Controller


def parse_arguments(argv):
    if argv is None:
        argv = sys.argv[1:]

    parser = ArgumentParser()
    parser.add_argument('ip')
    return parser.parse_args(argv)


def convert_steering(raw_steering):
    """ [-1, 1] -> [60, 120] """
    angle = int(round((raw_steering * 30) + 92))
    return angle


def convert_throttle(raw_throttle):
    # LEVEL1_SPEED = 10
    # LEVEL5_SPEED = 70
    # LEVEL2_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 1 + LEVEL1_SPEED)
    # LEVEL3_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 2 + LEVEL1_SPEED)
    # LEVEL4_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 3 + LEVEL1_SPEED)

    # lookup = [
    #     (0.2, LEVEL3_SPEED),
    #     (0.7, LEVEL4_SPEED),
    #     (0.9, LEVEL5_SPEED),
    # ]
    # if raw_throttle != 0:
    #     direction = raw_throttle / abs(raw_throttle)
    # else:
    #     direction = 1
    raw_throttle = abs(raw_throttle)
    if raw_throttle < 0.2:
        return 0, 1
    # for cutoff, speed in lookup:
    #     if raw_throttle > cutoff:
    #         return speed, direction
    # return 0, 1
    return 70, -1


def main(argv=None):
    options = parse_arguments(argv)

    controller = PS4Controller()
    controller.init()


    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((options.ip, 9999))
        axis_data = controller.listen()
        raw_steering = axis_data[0]
        raw_throttle = axis_data[4]
        converted_steering = str(convert_steering(raw_steering))
        converted_throttle, direction = convert_throttle(raw_throttle)
        converted_throttle = str(converted_throttle)
        if direction > 0:
            throttle_dir = 'f'
        else:
            throttle_dir = 'r'
        while len(converted_steering) < 3:
            converted_steering += ' '
        while len(converted_throttle) < 3:
            converted_throttle += ' '
        print(f'raw steering={raw_steering}, converted steering={converted_steering}')  # noqa: E501
        print(f'raw throttle={raw_throttle}, converted throttle={throttle_dir}{converted_throttle}')  # noqa: E501
        sock.send(f's {converted_steering} {throttle_dir} {converted_throttle}'.encode())
        sleep(0.05)


if __name__ == '__main__':
    sys.exit(main())
