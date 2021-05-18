from event import Event
from switch import Switch
from led import LED, Pattern
from video import Video
from webserver import WebServer
from dataserver import DataServer
from serial_task import SerialTask
from imu import IMU

import Jetson.GPIO as gpio

import time
import os

FRAME_SIZE = (3264, 2464)
FRAME_SIZE_2 = (FRAME_SIZE[0]/2, FRAME_SIZE[1]/2)
FRAME_SIZE_4 = (FRAME_SIZE[0]/4, FRAME_SIZE[1]/4)

#################
##    SETUP    ##
#################
gpio.cleanup()
gpio.setmode(gpio.BOARD)

gpio.setup(33, gpio.IN)
run_webserver = gpio.input(33)
run_webserver = False

s_record = Switch(35)

l_r = LED(23, color='red')
l_g = LED(21, color='green', initial_pattern=Pattern.BLINK)
l_r2 = LED(19, color='red', initial_pattern=Pattern.OFF)

if run_webserver:
    webserver = WebServer()
    dataserver = DataServer()

else:
    video = Video(display_size=FRAME_SIZE_4)

serial = SerialTask()
imu = IMU()

def start_video(event, args):
    global run_webserver
    if args['caller'] == s_record:
        l_r.pattern = Pattern.ON

        if run_webserver:
            webserver.stop(block=True)
            webserver.start(recording_size=FRAME_SIZE_4)

        else:
            video.start()

def stop_video(event, args):
    global run_webserver
    if args['caller'] == s_record:
        l_r.pattern = Pattern.OFF

        if run_webserver:
            webserver.stop(block=True)
            webserver.start(recording_size=None)

        else:
            video.stop()

def on_correct_serial_message(event, args):
    l_r2.blink = True

Event.register(s_record.EVENT_ON, start_video)
Event.register(s_record.EVENT_OFF, stop_video)
Event.register(SerialTask.EVENT_UPDATE, on_correct_serial_message)

if run_webserver:
    dataserver.start()

#################
## START TASKS ##
#################

l_g.start()
l_r.start()
l_r2.start()

s_record.start()

serial.start()

imu.start()

time.sleep(5)

i = None

while i != 'q':
    i = input("'q' to exit.")

print('Closing application.')

#################
##   CLEANUP   ##
#################
if run_webserver:
    webserver.stop()
    dataserver.stop()

s_record.stop()
l_r.stop()
l_g.stop()
l_r2.stop()
serial.stop()
imu.stop()
