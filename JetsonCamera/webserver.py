from pipeline import Pipeline
from event import Event
from task import Task

import uvicorn
from vidgear.gears.asyncio import WebGear
import cv2
from datetime import datetime


from threading import Thread
import time

class WebServer(Task):
    EVENT_INITIALIZED = Event.get_event_code('Webserver Initialized', verbose=True)
    EVENT_STARTED = Event.get_event_code('Webserver Started', verbose=True)
    EVENT_STOPPED = Event.get_event_code('Webserver Stopped', verbose=True)


    def __init__(self, host: str = '0.0.0.0', video_port: int = 8000, side_port: int = 8001, display_size: tuple = (3264/4, 2464/4)):
        self.host = host
        self.port = video_port
        self.side_port = side_port
        self.display_size=display_size

        self.thread = None

        self.options = {
            "frame_size_reduction": 40,
            "frame_jpeg_quality": 80,
            "frame_jpeg_optimize": True,
            "frame_jpeg_progressive": False
        }

        Event.dispatch(WebServer.EVENT_INITIALIZED, caller=self)

    def _task(self):
        self.server.run()

        self.web = None
        self.server = None

        Event.dispatch(WebServer.EVENT_STOPPED, caller=self)

    def start(self, filename: str = None, recording_size: tuple = None):
        if self.is_running():
            print('Webserver is already being running.')
            return

        if filename == None:
            date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'/home/oliver/Desktop/JetsonCamera/videos/{date}.yuv'

        pipeline = Pipeline(filename=filename, display_size=self.display_size, recording_size=recording_size)
        self.web = WebGear(source=pipeline.get_string(),
            resolution=self.display_size,
            backend=cv2.CAP_GSTREAMER,
            framerate=21,
            **self.options
        )

        config = uvicorn.Config(self.web(), host=self.host, port=self.port)
        self.server = uvicorn.Server(config)

        self._start()

    def stop(self, block: bool = False):
        if not self.is_running():
            print('Webserver isn\'t running.')
            return

        self.web.shutdown()
        self.server.should_exit = True
        
        self._stop()