import csv
import sys
import os.path
import http.client

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
import requests

from controller import PS4Controller

running_screen = "running_screen.ui"
Ui_Running_screen, QtBaseClass = uic.loadUiType(running_screen)

HOST = '10.0.0.3'
PORT = '8000'
BASE_URL = 'http://' + HOST + ':' + PORT + '/'


class RunningScreen(QtWidgets.QDialog, Ui_Running_screen):
    """Running Screen

    To creat a Graphical User Interface, inherit from
    Ui_Running_screen. And define functions that use for the control.

    Attributes:
            TIMEOUT, how long it time up for QTimer, using to reflash the frame
    """
    CONTROL_TIMEOUT = 5
    TIMEOUT = 50
    LEVEL1_SPEED = 40
    LEVEL5_SPEED = 100

    LEVEL2_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 1 + LEVEL1_SPEED)
    LEVEL3_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 2 + LEVEL1_SPEED)
    LEVEL4_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 3 + LEVEL1_SPEED)

    LEVEL_SPEED = [0, LEVEL1_SPEED, LEVEL2_SPEED, LEVEL3_SPEED,
                   LEVEL4_SPEED, LEVEL5_SPEED]

    def __init__(self, image_path, log_path):
        self.base_image_path = image_path
        self.log_path = log_path
        self.state = {'steering': 90, 'throttle': 0}
        QtWidgets.QDialog.__init__(self)
        Ui_Running_screen.__init__(self)
        self.image_counter = 0
        self.setupUi(self)
        self.controller = PS4Controller()
        self.controller.init()

        if not connection_ok():
            raise RuntimeError('Shit hit the fan yo')

    def start_stream(self):
        """Start to receive the stream

        With this function called, the QTimer start timing, while time
        up, call reflash_frame() function, the frame will be
        reflashed.

        Args:
                None
        """
        self.queryImage = QueryImage(HOST)
        self.video_timer = QTimer(timeout=self.reflash_frame)
        self.video_timer.start(RunningScreen.TIMEOUT)
        self.control_timer = QTimer(timeout=self.get_input)
        self.control_timer.start(RunningScreen.CONTROL_TIMEOUT)
        # init the position
        run_action('fwready')
        run_action('bwready')
        run_action('camready')

    def stop_stream(self):
        self.video_timer.stop()
        self.control_timer.stop()

    def get_input(self):
        axis_data = self.controller.listen()
        raw_steering = axis_data[0]
        raw_throttle = axis_data[4]
        converted_steering = self.convert_steering(raw_steering)
        converted_throttle = self.convert_throttle(raw_throttle)
        print(f'raw steering={raw_steering}, converted steering={converted_steering}')
        print(f'raw throttle={raw_throttle}, converted_throttle={converted_throttle}')
        run_speed(converted_throttle)
        direction = 1
        if raw_throttle < 0:
            direction = -1
            run_action('forward')
        elif raw_throttle > 0:
            direction = 1
            run_action('backward')
        else:
            run_action('stop')
        run_action(f'fwturn:{converted_steering}')
        self.state['throttle'] = direction * converted_throttle
        self.state['steering'] = converted_steering

    def convert_throttle(self, raw_throttle):
        """ [-1, 0] -> {0, 1, 2, 3, 4, 5} """
        lookup = [
            (0.2, self.LEVEL3_SPEED),
            (0.7, self.LEVEL4_SPEED),
            (0.9, self.LEVEL5_SPEED),
        ]
        raw_throttle = abs(raw_throttle)
        if raw_throttle < lookup[0][0]:
            return 0
        for cutoff, speed in lookup:
            if raw_throttle > cutoff:
                return speed
        return 0

    def convert_steering(self, raw_steering):
        """ [-1, 1] -> [45, 135] """
        return int(round((raw_steering * 45) + 90))

    def transToPixmap(self):
        """Convert the stream data to pixmap data

        First save the queryImage() data, and then creat an object
        pixmap, call built-in function pixmap.loadFromData(data) to
        store the data

        Args:
                None

        return:
                pixmap, the object of QPixmap()
                if no data, return None
        """
        # use the buile-in function to query image from http, and save in data
        data = self.queryImage.queryImage()
        image_path = os.path.join(self.base_image_path, f'{self.image_counter}.jpg')
        self.image_counter += 1
        with open(image_path, 'wb') as f:
            f.write(data)
        return image_path
        # if not data:
        #         return None
        # pixmap = QPixmap()
        # # get pixmap type data from http type data
        # pixmap.loadFromData(data)
        # return pixmap

    def reflash_frame(self):
        """Reflash frame on widget label_snapshot

        Use the return value of transToPixmap() to reflash the frame
        on widget label_snapshot

        Args:
                None
        """
        # this pixmap is the received and converted picture
        image_path = self.transToPixmap()
        with open(self.log_path, 'a') as f:
            log_writer = csv.writer(f)
            log_writer.writerow([
                image_path,
                self.state['throttle'],
                self.state['steering'],
            ])
        return image_path

        # if pixmap:
        #     # show the pixmap on widget label_snapshot
        #     self.label_snapshot.setPixmap(pixmap)
        # else:
        #     print("frame lost")


class QueryImage:
    """Query Image

    Query images form http. eg: queryImage = QueryImage(HOST)

    Attributes:
            host, port. Port default 8080, post need to set when creat
            a new object

    """
    def __init__(self, host, port=8080, argv="/?action=snapshot"):
        # default port 8080, the same as mjpg-streamer server
        self.host = host
        self.port = port
        self.argv = argv

    def queryImage(self):
        """Query Image

        Query images form http.eg:data = queryImage.queryImage()

        Args:
                None

        Return:
                returnmsg.read(), http response data
        """
        http_data = http.client.HTTPConnection(self.host, self.port)
        http_data.putrequest('GET', self.argv)
        http_data.putheader('Host', self.host)
        http_data.putheader('User-agent', 'python-http.client')
        http_data.putheader('Content-type', 'image/jpeg')
        http_data.endheaders()
        returnmsg = http_data.getresponse()

        return returnmsg.read()


def connection_ok():
    """Check whetcher connection is ok

    Post a request to server, if connection ok, server will return
    http response 'ok'

    Args:
            none

    Returns:
            if connection ok, return True
            if connection not ok, return False

    Raises:
            none
    """
    cmd = 'connection_test'
    url = BASE_URL + cmd
    print(f'url: {url}')
    # if server find there is 'connection_test' in request url, server
    # will response 'Ok'
    try:
        r = requests.get(url)
        if r.text == 'OK':
            return True
    except:
        return False


def __request__(url, times=10):
    for x in range(times):
        try:
            requests.get(url)
            return 0
        except:
            print("Connection error, try again")
    print("Abort")


def run_action(cmd):
    """Ask server to do sth, use in running mode

    Post requests to server, server will do what client want to do
    according to the url.  This function for running mode

    Args:
            # ============== Back wheels =============
            'bwready' | 'forward' | 'backward' | 'stop'

            # ============== Front wheels =============
            'fwready' | 'fwleft' | 'fwright' |  'fwstraight'

            # ================ Camera =================
            'camready' | 'camleft' | 'camright' | 'camup' | 'camdown'
    """
    # set the url include action information
    url = BASE_URL + 'run/?action=' + cmd
    print(f'url: {url}')
    # post request with url
    __request__(url)


def run_speed(speed):
    """Ask server to set speed, use in running mode

    Post requests to server, server will set speed according to the url.
    This function for running mode.

    Args:
            '0'~'100'
    """
    # Set set-speed url
    url = f'{BASE_URL}run/?speed={speed}'
    print(f'url: {url}')
    # Set speed
    __request__(url)


def app():
    app = QtWidgets.QApplication(sys.argv)
    image_path = sys.argv[1]
    log_path = sys.argv[2]

    # creat objects
    running1 = RunningScreen(image_path, log_path)
    running1.start_stream()
    running1.show()

    app.exec_()


if __name__ == '__main__':
    app()
