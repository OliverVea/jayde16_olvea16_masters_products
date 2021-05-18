from event import Event
from task import Task

from led import LED
from switch import Switch
from video import Video
from webserver import WebServer

from threading import Thread
import websockets
import json
import asyncio
import datetime
import random
from queue import Queue

# DO this with websockets instead OOOOO DUMBFUUUUUUCK

connections = {}
async def time(websocket, path):
    global connections

    remote_addr, remote_port = websocket.remote_address
    server_addr, server_port = websocket.local_address

    key = (server_addr, server_port, remote_addr, remote_port)

    connections[key] = Queue()

    while connections[key] != None:
        while not connections[key].empty():
            message = connections[key].get(block=False)
            await websocket.send(message)

        await asyncio.sleep(0.1)

class DataServer(Task):
    EVENT_INITIALIZED = Event.get_event_code('Dataserver Initialized', verbose=False)
    EVENT_STARTED = Event.get_event_code('Dataserver Started', verbose=False)
    EVENT_STOPPED = Event.get_event_code('Dataserver Stopped', verbose=False)

    EVENT_UPDATE = Event.get_event_code('Dataserver Update', verbose=True)

    UPDATE_SET = 0
    UPDATE_ADD = 1
    UPDATE_REMOVE = 2

    def __init__(self, host: str = '', port: int = 8001):
        self.host = host
        self.port = 8001

        self.thread = None
        self.connections = {}

        Event.register(Switch.EVENT_CHANGED, lambda event, args: self._send_update(event, args))

        self.state = {
            'fps': 21,
            'leds': {}, # 13: {'color': 'red', 'pattern': 'blink'} (pin: {})
            'switches': {}, # 35: {'state': on}
        }

    def _event_handler(event, caller):
        if event == Switch.EVENT_STARTED:
            update = {'switches': {caller.pin: {caller.state}}}
            self._send_update(self.TYPE_ADD, update)

        elif event == Switch.EVENT_STOPPED:
            pass

        elif event == Switch.EVENT_CHANGED:
            pass

    def _get_update(self):
        pass

    # 2 messages: add and remove
    def _send_update(self, event: int, args: dict):
        message = ""
        #message = json.dumps(update)

        for key, queue in zip(connections.keys(), connections.values()):
            queue.put(message)

    def _message_handler(self):
        pass

    def _task(self):
        try:
            loop = asyncio.get_event_loop()

        except RuntimeError as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        start_server = websockets.serve(time, '', 8001)

        loop.run_until_complete(start_server)
        loop.run_forever()

    def start(self):
        self._start()
        
    def stop(self):
        self._stop()