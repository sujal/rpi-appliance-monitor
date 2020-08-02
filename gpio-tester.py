#!/usr/bin/python

import sys
import time
import logging
import threading
import RPi.GPIO as GPIO
from time import localtime, strftime

from ConfigParser import SafeConfigParser

def vibrated(x):
    global vibrating
    global last_vibration_time
    global start_vibration_time
    logging.info('Vibrated')
    last_vibration_time = time.time()
    if not vibrating:
        start_vibration_time = last_vibration_time
        vibrating = True


def heartbeat():
    current_time = time.time()
    logging.info("HB at {}".format(current_time))
    global vibrating
    global appliance_active
    delta_vibration = last_vibration_time - start_vibration_time
    if (vibrating and delta_vibration > begin_seconds
            and not appliance_active):
        logging.info("Would've sent the active message")
        appliance_active = True
    if (not vibrating and appliance_active
            and current_time - last_vibration_time > end_seconds):
        logging.info("Would've sent the inactive message")
        appliance_active = False
    vibrating = current_time - last_vibration_time < 2
    threading.Timer(1, heartbeat).start()


logging.basicConfig(format='%(message)s', level=logging.INFO)

if len(sys.argv) == 1:
    logging.critical("No config file specified")
    sys.exit(1)

vibrating = False
appliance_active = False
last_vibration_time = time.time()
start_vibration_time = last_vibration_time

config = SafeConfigParser()
config.read(sys.argv[1])
sensor_pin = config.getint('main', 'SENSOR_PIN')
begin_seconds = config.getint('main', 'SECONDS_TO_START')
end_seconds = config.getint('main', 'SECONDS_TO_END')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(sensor_pin, GPIO.RISING)
GPIO.add_event_callback(sensor_pin, vibrated)

logging.info('Running config file {} monitoring GPIO pin {}'\
      .format(sys.argv[1], str(sensor_pin)))
threading.Timer(1, heartbeat).start()
