# -*- coding: utf-8 -*-
#
# This file presents an interface for interacting with the Playstation
# 4 Controller in Python. Simply plug your PS4 controller into your
# computer using USB and run this script!
#
# NOTE: I assume in this script that the only joystick plugged in is
#       the PS4 controller.  if this is not the case, you will need to
#       change the class accordingly.
#
# Copyright © 2015 Clay L. McLeod <clay.l.mcleod@gmail.com>
#
# Distributed under terms of the MIT license.

from collections import defaultdict
import time

import pygame


class PS4Controller:
    """Class representing the PS4 controller. Pretty straightforward
        functionality.

    """

    controller = None

    def init(self):
        """Initialize the joystick components"""

        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        self.axis_data = defaultdict(int)

    def listen(self):
        """Listen for events to happen"""

        start_millis = int(round(time.time() * 1000))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = round(event.value, 2)
                    return self.axis_data
                now_millis = int(round(time.time() * 1000))
                if now_millis - start_millis > 4:
                    return self.axis_data


if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    while True:
        print(ps4.listen())
