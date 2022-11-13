#!/bin/python3

# Check for the trigger line on  GPIO 16

import RPi.GPIO as GPIO
import signal
import sys

import time
from time import sleep

trigcnt = 0

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def exti_callback(channel):
    # When trigger arrives, increment triger count and request image capture
    global trigcnt
    trigcnt += 1
    print("Trigger: {}".format(trigcnt))

#### Initialize GPIO interrupt
EXTI_GPIO = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(EXTI_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(EXTI_GPIO, GPIO.RISING, 
    callback=exti_callback, bouncetime=200)

signal.signal(signal.SIGINT, signal_handler) # Catch Ctrl+c for cleanup

while True:
    sleep(1)
