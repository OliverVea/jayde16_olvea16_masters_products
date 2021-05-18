from event import Event
from pipeline import Pipeline
from serial_task import SerialTask

import time
import os

from threading import Thread
from datetime import datetime
import cv2
from PIL import Image

class Video:
    EVENT_INITIALIZED = Event.get_event_code('Video Initialized', verbose=True)
    EVENT_STARTED = Event.get_event_code('Video Started', verbose=True)
    EVENT_STOPPED = Event.get_event_code('Video Stopped', verbose=True)
    EVENT_NEW_FRAME = Event.get_event_code('New Video Frame', verbose=False)

    def __init__(self, recording_size: tuple = None, display_size: tuple = None, file_delimiter: str = ','):
        self.recording_size = recording_size
        self.display_size = display_size
        self.delimiter = file_delimiter
        self.thread = None

        self.last_message = ''

        Event.dispatch(Video.EVENT_INITIALIZED, caller=self)

        def set_last_message(event, args):
            self.last_message = args['message']

        Event.register(SerialTask.EVENT_UPDATE, set_last_message)

    def _task(self):
        vc = cv2.VideoCapture(self.pipeline.get_string(), cv2.CAP_GSTREAMER)

        print('displaying:', self.pipeline.displaying)

        if self.pipeline.displaying:

            then = time.time()
            fps = 21

            font                   = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfText = (2, 14)
            fontScale              = 0.5
            fontColor              = (255,255,255)
            lineType               = 2

        while self.running:
            ret_val, img = vc.read()
            Event.dispatch(Video.EVENT_NEW_FRAME, caller=self, ret_val=ret_val, img=img)

            cv2.imwrite(f'{self.path}/{self.i}.png', img)
            
            with open(self.data_file, 'a') as f:
                line = [str(self.i), str(time.time()), self.last_message]
                line = self.delimiter.join(line)
                f.write(line + '\n')

            self.i += 1
            time.sleep(0.2)
        
        vc.release()
        cv2.destroyAllWindows()

    def is_running(self):
        return self.thread != None

    def start(self, sequence_name: str = None):    
        if self.is_running():
            print('Video is already being recorded.')
            return

        if sequence_name == None:
            sequence_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        path = f'/home/oliver/Desktop/JetsonCamera/videos/{sequence_name}'

        os.makedirs(path)

        self.path = path
        self.pipeline = Pipeline(display_size=self.display_size)
        self.running = True

        self.i = 0

        self.data_file = f'/home/oliver/Desktop/JetsonCamera/gps/{sequence_name}.csv'
        with open(self.data_file, 'w') as f:
            f.write(self.delimiter.join(['i', 'time', 'message']) + '\n')

        self.last_message = ''

        self.thread = Thread(target=Video._task, args=(self,))
        self.thread.start()

        Event.dispatch(Video.EVENT_STARTED, caller=self)

    def stop(self):
        if not self.is_running():
            print(f'Video is already not being recorded.')
            return

        self.running = False

        self.thread.join()
        self.thread = None

        Event.dispatch(Video.EVENT_STOPPED, caller=self, filename=self.filename)