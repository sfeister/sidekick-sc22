#!/bin/python3

# Copied from picamera2 user guide

from picamera2 import Picamera2, Preview
import time

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
#picam2.start_preview(Preview.QTGL) # for live preview
picam2.start_preview(Preview.QT) # for VNC preview
picam2.start()
time.sleep(100)
picam2.capture_file("/home/pi/images/test.jpg")
