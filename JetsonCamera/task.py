from threading import Thread
from event import Event

class Task:
    def is_running(self):
        return self.thread != None

    def _stop(self, dispatch_event: bool = True):
        if not self.is_running():
            print('Could not stop thread, as it is not running.')
            return

        self.running = False
        self.thread.join()
        self.thread = None

        if dispatch_event:
            Event.dispatch(self.EVENT_STOPPED, caller=self)

    def _start(self, dispatch_event: bool = True):
        if self.is_running():
            print('Could not start thread, as it is already running.')
            return

        self.running = True
        self.thread = Thread(target=self._task, args=())
        self.thread.start()

        if dispatch_event:
            Event.dispatch(self.EVENT_STARTED, caller=self)

