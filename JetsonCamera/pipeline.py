class Pipeline:
    @staticmethod
    def _get_source(width, height, framerate):
        return  [
            f'nvarguscamerasrc', 
            f'video/x-raw(memory:NVMM), width=(int){int(width)}, height=(int){int(height)}, format=(string)NV12, framerate=(fraction){framerate}/1'
        ]

    @staticmethod
    def _get_filesink(width, height, filename):
        return [
            f'nvvidconv', 
            f'video/x-raw, width=(int){int(width)}, height=(int){int(height)}, format=(string)I420', 
            f'y4menc', 
            f'filesink location={filename}'
        ]

    @staticmethod
    def _get_appsink(width, height, max_buffers: int = 1, drop: bool = True):
        return [
            f'nvvidconv',
            f'video/x-raw, width=(int){int(width)}, height=(int){int(height)}, format=(string)BGRx',
            f'videoconvert',
            f'video/x-raw, format=(string)BGR',
            f'appsink max-buffers=1 drop={str(drop).lower()}'
        ]

    def _set_display_options(self, display_size):
        self.displaying = (display_size != None)
        if self.displaying:
            self.display_width, self.display_height = display_size

    def _set_recording_options(self, recording_size, filename):
        self.recording = (recording_size != None and filename != None)
        if self.recording:
            self.recording_width, self.recording_height = recording_size
        self.filename = filename

    def _is_branching(self):
        return self.displaying and self.recording

    def __init__(self, capture_size: tuple = (3264, 2464), display_size: tuple = None, recording_size: tuple = None, filename: str = None, framerate: int = 21):
        self.capture_width, self.capture_height = capture_size
        self.framerate = framerate

        self._set_display_options(display_size)
        self._set_recording_options(recording_size, filename)

    def get_string(self):
        source = Pipeline._get_source(self.capture_width, self.capture_height, self.framerate)

        s = ' ! '.join(source)

        if self._is_branching():

            appsink = Pipeline._get_appsink(self.display_width, self.display_height)
            filesink = Pipeline._get_filesink(self.recording_width, self.recording_height, self.filename)
            
            s = ' ! '.join([s, 'tee name=t', 'queue'] + appsink) + ' ! '.join([' t.', 'queue'] + filesink)

        else:
            if self.recording:
                filesink = Pipeline._get_filesink(self.recording_width, self.recording_height, self.filename)
                s = ' ! '.join([s] + filesink)

            else:
                appsink = Pipeline._get_appsink(self.display_width, self.display_height)
                s = ' ! '.join([s] + appsink)

        return s
