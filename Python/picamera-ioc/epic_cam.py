from picamera2 import Picamera2, Preview
import time
import logging


class epic_camera:
    def __init__(self):
        self.picam2 = Picamera2()
        self.camera_config = self.picam2.create_still_configuration(main={"size":(1920, 1080)}, lores={"size":(640, 480)}, display="lores")
    def start(self):
        self.picam2.configure(self.camera_config)
        #self.picam2.start_preview(Preview.QTGL)
        self.picam2.start()
        #while True:
        #  time.sleep(1)
    def take_snapshot(self):
        print("Taking a snapshot")
        self.picam2.capture_file("test.bmp")
    def stop(self):
        self.picam2.stop()
        #self.picam2.stop_preview()
