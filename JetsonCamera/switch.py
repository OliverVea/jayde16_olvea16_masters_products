from event import Event
from task import Task

import Jetson.GPIO as gpio
from threading import Thread
import time

class Switch(Task):
    EVENT_INITIALIZED = Event.get_event_code('Switch Initialized', verbose=True)
    EVENT_STARTED = Event.get_event_code('Switch Started', verbose=True)
    EVENT_STOPPED = Event.get_event_code('Switch Stopped', verbose=True)
    EVENT_CHANGED = Event.get_event_code('Switch Changed', verbose=True)
    EVENT_ON = Event.get_event_code('Switch On', verbose=False)
    EVENT_OFF = Event.get_event_code('Switch Off', verbose=False)

    def __init__(self, pin_number, pin_cleanup: int = 1, sample_frequency: float = 50, debounce_delay: float = 0.05):
        self.pin = pin_number
        self.cleanup = pin_cleanup
        self.sample_period = 1 / sample_frequency
        self.delay = debounce_delay

        self.running = False
        self.state = -1
        self.thread = None

        Event.dispatch(Switch.EVENT_INITIALIZED, pin=pin_number, caller=self)

    def __del__(self):
        if self.cleanup >= 1:
            gpio.cleanup(self.pin)

    def _update(self, state):
        if state != self.state:
            Event.dispatch(Switch.EVENT_CHANGED, state=state, previous_state=self.state, caller=self)

            self.state = state

            if state:
                Event.dispatch(Switch.EVENT_ON, caller=self)
            else:
                Event.dispatch(Switch.EVENT_OFF, caller=self)

            if self.delay > 0:
                time.sleep(self.delay)

    def _task(self):
        while self.running:
            try:
                state = gpio.input(self.pin)
                self._update(state)
            except: pass

            time.sleep(self.sample_period)

    def start(self):
        if self.is_running():
            print(f'Could not start Switch thread (pin {self.pin}) as it is already running.')
            return

        gpio.setup(self.pin, gpio.IN)
        state = gpio.input(self.pin)
        self._update(state)

        self._start()

    def stop(self):
        self._stop()

        if self.cleanup >= 2:
            gpio.cleanup(self.pin)

        self.state = -1