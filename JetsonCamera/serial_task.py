from task import Task
from event import Event

import time
import serial
from serial.tools import list_ports

import pynmea2

class SerialTask(Task):
    EVENT_INITIALIZED = Event.get_event_code('Serial Initialized', verbose=True)
    EVENT_STARTED = Event.get_event_code('Serial Started', verbose=True)
    EVENT_STOPPED = Event.get_event_code('Serial Stopped', verbose=True)

    EVENT_UPDATE = Event.get_event_code('Serial Update', verbose=False)

    def __init__(self, sensor_name: str = 'AH01ED0D'):
        self.thread = None
        self.last_update = time.time()
        self.sensor_name = sensor_name

    def _task(self):
        while self.running:
            try:
                ports = {p.serial_number:p.device for p in list_ports.comports() if p.serial_number}

                if not self.sensor_name in ports:
                    time.sleep(2)
                    continue

                port = ports[self.sensor_name]

                with serial.Serial(port, 115200, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, timeout=1) as ser:
                    line = ser.readline()

                    try:
                        message = line.decode('utf-8').strip()
                        decoded_message = pynmea2.parse(message)

                        if pynmea2.parse(message).is_valid:
                            if time.time() - self.last_update >= 0.2:
                                Event.dispatch(SerialTask.EVENT_UPDATE, caller=self, message=message)
                                self.last_update = time.time()

                    # Decoding error.
                    except UnicodeDecodeError as e:
                        #print(f'Decode error: {e}')
                        pass

                    # Error in parsing message.
                    except pynmea2.ParseError as e:
                        #print(f'Parse error: {e}')
                        pass
                            
                    except Exception as e:
                        print(e)
                        pass

            # If the serial device isn't available
            except serial.serialutil.SerialException as e:
                time.sleep(2)

            except OSError as e:
                #print(e)
                time.sleep(2)


    def start(self):
        self._start()

    def stop(self):
        self._stop()
