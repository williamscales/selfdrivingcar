import asyncio
import concurrent.futures
import csv
import logging
import os
import sys
import time

from PIL import Image
from PyV4L2Camera.camera import Camera
from picar.SunFounder_PCA9685 import Servo
from picar.SunFounder_TB6612 import TB6612
from picar.SunFounder_PCA9685 import PCA9685

START_TIME = str(time.time()).split('.')[0]

steering_value = None
throttle_value = None


def do_initial_setup():
    pwm = PCA9685.PWM(bus_number=1)
    pwm.setup()
    pwm.frequency = 60


def get_uvc_device():
    return Camera('/dev/video0', 640, 480)


def get_frame_path():
    frame_path_base = 'frames'
    return f'{frame_path_base}-{START_TIME}'


def get_log_writer():
    log_file = open(f'log-{START_TIME}.csv', 'w')
    fieldnames = ['frame_filename', 'steering_value', 'throttle_value']
    log_writer = csv.DictWriter(log_file, fieldnames=fieldnames)
    log_writer.writeheader()
    return log_writer


def get_uvc_frame(uvc_device, frame_path, log_writer):
    global steering_value, throttle_value
    start_time = time.time()
    frame = uvc_device.get_frame()
    im = Image.frombytes(
        'RGB', (uvc_device.width, uvc_device.height), frame, 'raw', 'RGB'
    )
    frame_number = str(time.time()).replace('.', '')
    frame_filename = os.path.join(frame_path, f'{frame_number}.jpg')
    im.save(frame_filename)
    log_writer.writerow({
        'frame_filename': frame_filename,
        'steering_value': steering_value,
        'throttle_value': throttle_value,
    })
    end_time = time.time()
    return f'frame size was ({uvc_device.width}, {uvc_device.height}), took {(end_time - start_time) * 1000:4.4} ms'  # noqa: E501


async def save_frame(executor, uvc_device, frame_path, log_writer):
    log = logging.getLogger('save_frame')
    log.info(f'starting')
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(
            executor,
            get_uvc_frame,
            uvc_device,
            frame_path,
            log_writer,
        )
    ]
    log.info('waiting for frame')
    completed, pending = await asyncio.wait(tasks)
    for future in completed:
        log.info(future.result())


async def frame_scheduler(executor, uvc_device, frame_path, log_writer):
    log = logging.getLogger('frame_scheduler')
    log.info('starting')
    loop = asyncio.get_event_loop()
    while True:
        loop.create_task(save_frame(
            executor=executor,
            uvc_device=uvc_device,
            frame_path=frame_path,
            log_writer=log_writer,
        ))
        await asyncio.sleep(0.1)


def get_front_wheel():
    channel = 0
    bus_number = 1
    return Servo.Servo(channel, bus_number=bus_number, offset=0)


def get_rear_wheels():
    left_wheel = TB6612.Motor(17, offset=1)
    right_wheel = TB6612.Motor(27, offset=1)
    pwm = PCA9685.PWM(bus_number=1)

    def _set_a_pwm(value):
        pulse_wide = int(pwm.map(value, 0, 100, 0, 4095))
        pwm.write(4, 0, pulse_wide)

    def _set_b_pwm(value):
        pulse_wide = int(pwm.map(value, 0, 100, 0, 4095))
        pwm.write(5, 0, pulse_wide)

    left_wheel.pwm = _set_a_pwm
    right_wheel.pwm = _set_b_pwm
    return left_wheel, right_wheel


def get_command_lookup_table():
    front_wheel = get_front_wheel()
    rear_wheels = get_rear_wheels()

    return {
        's': steer(front_wheel),
        'f': throttle(rear_wheels, reverse=False),
        'r': throttle(rear_wheels, reverse=True),
    }


def steer(wheel):
    def inner(angle):
        global steering_value
        wheel.write(int(angle))
        steering_value = int(angle)
        return f'setting steering_value to {int(angle)}'
    return inner


def throttle(wheels, reverse=False):
    def inner(amount):
        global throttle_value
        if reverse:
            for wheel in wheels:
                wheel.backward()
        else:
            for wheel in wheels:
                wheel.forward()
        for wheel in wheels:
            wheel.speed = int(amount)
        throttle_value = int(amount)
        return f'setting throttle_value to {int(amount)}'
    return inner


def parse_message(message):
    parts = iter(message.split())
    return [
        (command, [float(next(parts))])
        for command in parts
    ]


async def dispatch_command(lookup_table, executor, message):
    log = logging.getLogger('dispatch_command')

    commands = parse_message(message)

    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(
            executor,
            lookup_table[command],
            *command_args,
        )
        for command, command_args in commands
    ]
    completed, _ = await asyncio.wait(tasks)
    for future in completed:
        log.info(future.result())


def command_server(executor, lookup_table):
    async def inner(reader, writer):
        log = logging.getLogger('command_server')
        log.info('starting')
        data = await reader.read(10)
        message = data.decode().strip()
        addr = writer.get_extra_info('peername')
        log.info(f'received "{message}" from "{addr[0]}:{addr[1]}"')
        await dispatch_command(lookup_table, executor, message)
    return inner


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(threadName)10s %(name)18s: %(message)s',
        stream=sys.stderr,
    )

    do_initial_setup()

    camera = get_uvc_device()
    # camera = None
    command_table = get_command_lookup_table()
    frame_path = get_frame_path()
    if not os.path.exists(frame_path):
        os.makedirs(frame_path)
    log_writer = get_log_writer()

    camera_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    command_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    event_loop = asyncio.get_event_loop()
    server = command_server(command_pool, command_table)
    command_coro = asyncio.start_server(
        server,
        '',
        9999,
        loop=event_loop,
    )
    command_server = event_loop.run_until_complete(command_coro)

    event_loop.run_until_complete(
        frame_scheduler(
            executor=camera_pool,
            uvc_device=camera,
            frame_path=frame_path,
            log_writer=log_writer,
        )
    )

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        command_server.close()
        event_loop.run_until_complete(command_server.wait_closed())
        event_loop.close()
