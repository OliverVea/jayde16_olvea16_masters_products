from event import Event
from task import Task

from vnpy import VnSensor

from serial.tools import list_ports

import time
from datetime import datetime

class IMU(Task):
    EVENT_INITIALIZED = Event.get_event_code('IMU Initialized', verbose=True)
    EVENT_STARTED = Event.get_event_code('IMU Started', verbose=True)
    EVENT_STOPPED = Event.get_event_code('IMU Stopped', verbose=True)

    def __init__(self, file_name: str = '', sensor_name='FTUBIB6L', baud_rate: int = 115200):
        self.sensor_name = sensor_name
        self.baud_rate = baud_rate

        if file_name == '':
            file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        self.path = f'/home/oliver/Desktop/JetsonCamera/imu/{file_name}.txt'

        self.running = False
        self.thread = None

        Event.dispatch(IMU.EVENT_INITIALIZED, caller=self)

    def _task(self):
        while self.running:
            ports = {p.serial_number:p.device for p in list_ports.comports() if p.serial_number}

            if not self.sensor_name in ports:
                time.sleep(2)
                continue

            port = ports[self.sensor_name]

            try:
                sensor = VnSensor()
                sensor.connect(port, self.baud_rate)

                while self.running:
                    acceleration = list(sensor.read_acceleration_measurements())
                    angular_rate = list(sensor.read_angular_rate_measurements())
                    mag = list(sensor.read_magnetic_measurements())
                    ypr = list(sensor.read_yaw_pitch_roll())

                    if self.first:
                        header = ['time']
                        header += [f'acceleration_{i}' for i in range(len(acceleration))]
                        header += [f'angular_rate_{i}' for i in range(len(angular_rate))]
                        header += [f'magnetic_{i}' for i in range(len(mag))]
                        header += [f'yaw_pitch_roll_{i}' for i in range(len(ypr))]

                        with open(self.path, 'w') as f:
                            header = ';'.join([str(e) for e in header])
                            f.write(header + '\n')

                        self.first = False

                    with open(self.path, 'a') as f:
                        measurements = [time.time()] + acceleration + angular_rate + mag + ypr
                        measurements = ';'.join([str(e) for e in measurements])
                        f.write(measurements + '\n')

                    time.sleep(0.005)

            except Exception as e:
                print('EXCEPTION!')
                print(e)

    def start(self):
        if self.is_running():
            print(f'Could not start IMU thread as it is already running.')
            return

        self.first = True

        self._start()

    def stop(self):
        self._stop()
