#!/bin/python3

from picamera2 import Picamera2, Preview
import time
from time import sleep
from PIL import Image
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from softioc import softioc, builder
import cothread
import logging

def getbox(x, y, rad=50):
    """ Gets a matplotlib patch and a PIL-style crop box from x,y center coordinates and an optional half-diameter"""
    xycent = np.array([x, y])
    xy = xycent - rad
    width = rad*2
    height = rad*2

    rect_patch = mpl.patches.Rectangle(xy, width, height)
    box_PIL = (xy[0], xy[1], xy[0]+height, xy[1] + width) # left, upper, right, lower
    return box_PIL, rect_patch

if __name__ == "__main__":
    ### INITIALIZE EPICS SERVER
    logging.basicConfig(level=logging.DEBUG)

    # Set the record prefix
    builder.SetDeviceName("CAM")

    ## Create some records
    cam_info = builder.stringIn("INFO", initial_value="DolphinDAQ,PiCamera2,#00,20221112-5AM")

    # Run contols
    cam_enable = builder.boolOut("ENABLE", ZNAM="false", ONAM="true")
    cam_debug = builder.boolOut("DEBUG:ENABLE", ZNAM="false", ONAM="true")

    # Run status
    cam_starting = builder.boolIn("STARTING", ZNAM="false", ONAM="true")
    cam_running = builder.boolIn("RUNNING", ZNAM="false", ONAM="true")
    cam_stopping = builder.boolIn("STOPPING", ZNAM="false", ONAM="true")

        # Format e.g. "TRIG:412302132,R:25,G:205,B:111"
    roi1_data = builder.stringIn("ROI1:DATA", initial_value="")
    roi1_x = builder.longOut("ROI1:X", initial_value=310)
    roi1_y = builder.longOut("ROI1:Y", initial_value=410)
    roi1_rad = builder.longOut("ROI1:RAD", initial_value=10)

    roi2_data = builder.stringIn("ROI2:DATA", initial_value="")
    roi2_x = builder.longOut("ROI2:X", initial_value=990)
    roi2_y = builder.longOut("ROI2:Y", initial_value=390)
    roi2_rad = builder.longOut("ROI2:RAD", initial_value=10)

    # Boilerplate get the IOC started
    builder.LoadDatabase()
    softioc.iocInit()

    ### INITIALIZE CAMERA
    print("Starting the camera.")
    cam_starting.set(1)
    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration()
    picam2.configure(camera_config)
    print("CAMERA CONFIGURATION:")
    print(camera_config)
    picam2.start()
    cam_starting.set(0)
    cam_running.set(1)

    trigcnt = 1828398

    while True:
        ## CAPTURE A SINGLE IMAGE (todo: move this into a callback)
        
        # TODO: Await a new trigger here
        # TODO: Exposure issues?
        
        trigcnt += 1
        
        im = picam2.capture_image("main")
        imarr = np.array(im)

        # Hard code positions of rectangles here!
        #box1, rect1 = getbox(x=309, y=438, rad=10);
        #box2, rect2 = getbox(x=990, y=389, rad=10);
        box1, rect1 = getbox(x=roi1_x.get(), y=roi1_y.get(), rad=roi1_rad.get());
        box2, rect2 = getbox(x=roi2_x.get(), y=roi2_y.get(), rad=roi2_rad.get());
        #print(box1)

        im1 = im.crop(box=box1)
        im1_arr = np.array(im1)[:,:,:3] # Note, remove transparency channel here
        avg1 = im1_arr.mean(axis=(0,1))
        avg1_u8 = np.round(avg1).astype(np.uint8)
        datastr1 = "TRIG:{},R:{},G:{},B:{}".format(trigcnt,avg1_u8[0],avg1_u8[1],avg1_u8[2])
        roi1_data.set(datastr1)

        im2 = im.crop(box=box2)
        im2_arr = np.array(im2)[:,:,:3] # Note, remove transparency channel here
        avg2 = im2_arr.mean(axis=(0,1))
        avg2_u8 = np.round(avg2).astype(np.uint8)
        datastr2 = "TRIG:{},R:{},G:{},B:{}".format(trigcnt,avg2_u8[0],avg2_u8[1],avg2_u8[2])
        roi2_data.set(datastr2)
        print(datastr1)
        #print(datastr2)
        
        if cam_debug.get():
            print("Saving photo for trigger {}".format(trigcnt))
            # Save photo
            im.save('/home/pi/images/{}-photo.png'.format(trigcnt))

            # Save graphic patched over with ROI rectangles
            fig, ax = plt.subplots()
            ax.imshow(imarr)
            ax.add_patch(rect1)
            ax.add_patch(rect2)
            fig.savefig('/home/pi/images/{}-patched.png'.format(trigcnt))
            fig.clear()

        sleep(1)
    
    #sleep(20)
    # Finally leave the IOC running with an interactive shell.
    #softioc.interactive_ioc(globals())
    cothread.WaitForQuit()

