#!/bin/python3
# Checking for trigger from PulseGenerator

# External module imports
import RPi.GPIO as GPIO
import time
from time import sleep

# Pin Definitons:
pin = 23 # Broadcom pin 23 (P1 pin 16)
trigCount = 0 # trigger count

# Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(pin, GPIO.IN) # LED pin set as input

print("Here we go! Press CTRL+C to exit")
try:
    while 1:
        if GPIO.input(pin): # pin 16 is triggered
            print(trigCount);
            trigCount = trigCount + 1
        sleep(1)
            
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    GPIO.cleanup() # cleanup all GPIO
