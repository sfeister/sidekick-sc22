#!/bin/python3

# An untested effort to tie everything together

from picamera2 import Picamera2, Preview
from picamera2.controls import Controls
import time
from time import sleep
from PIL import Image
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import RPi.GPIO as GPIO
import signal
import sys

from softioc import softioc, builder
import cothread
import logging

trigcnt = 0
capture = False
exp_us = 10000 # initial exposure

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def exti_callback(channel):
    # When trigger arrives, increment triger count and request image capture
    global trigcnt, capture
    trigcnt += 1
    if not capture:
        capture = True

def update_trigcnt(value):
    global trigcnt
    trigcnt = value

def getbox(x, y, rad=50):
    """ Gets a matplotlib patch and a PIL-style crop box from x,y center coordinates and an optional half-diameter"""
    xycent = np.array([x, y])
    xy = xycent - rad
    width = rad*2
    height = rad*2

    rect_patch = mpl.patches.Rectangle(xy, width, height, ec="red", fill=False)
    box_PIL = (xy[0], xy[1], xy[0]+height, xy[1] + width) # left, upper, right, lower
    return box_PIL, rect_patch

if __name__ == "__main__":
    ### INITIALIZE EPICS SERVER
    logging.basicConfig(level=logging.DEBUG)

    # Set the record prefix
    builder.SetDeviceName("CAM")

    ## Create some records
    cam_info = builder.stringIn("info", initial_value="DolphinDAQ,PiCamera2,#00,20230323")

    # Run contols
    cam_enable = builder.boolOut("ENABLE", ZNAM="false", ONAM="true")
    cam_debug = builder.boolOut("DEBUG:ENABLE", ZNAM="false", ONAM="true", initial_value=0)

    # Run status
    cam_starting = builder.boolIn("STARTING", ZNAM="false", ONAM="true")
    cam_running = builder.boolIn("RUNNING", ZNAM="false", ONAM="true")
    cam_stopping = builder.boolIn("STOPPING", ZNAM="false", ONAM="true")

    cam_exposure = builder.longOut("EXPOSURE", initial_value=exp_us)
    cam_trigcnt = builder.longOut("TRIGCNT", initial_value=trigcnt, on_update=update_trigcnt)
        
    # Format e.g. "TRIG:412302132,R:25,G:205,B:111"
    roi1_data = builder.stringIn("ROI1:DATA", initial_value="")
    roi1_x = builder.longOut("ROI1:X", initial_value=128)
    roi1_y = builder.longOut("ROI1:Y", initial_value=298)
    roi1_rad = builder.longOut("ROI1:RAD", initial_value=10)
    roi1_bg_r = builder.longOut("ROI1:BG:red", initial_value=0)
    roi1_bg_g = builder.longOut("ROI1:BG:green", initial_value=0)
    roi1_bg_b = builder.longOut("ROI1:BG:blue", initial_value=0)
            
    
    roi2_data = builder.stringIn("ROI2:DATA", initial_value="")
    roi2_x = builder.longOut("ROI2:X", initial_value=1131)
    roi2_y = builder.longOut("ROI2:Y", initial_value=298)
    roi2_rad = builder.longOut("ROI2:RAD", initial_value=10)
    roi2_bg_r = builder.longOut("ROI2:BG:red", initial_value=0)
    roi2_bg_g = builder.longOut("ROI2:BG:green", initial_value=0)
    roi2_bg_b = builder.longOut("ROI2:BG:blue", initial_value=0)
    
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
    
    # Adjust exposure time
    ctrls = Controls(picam2)
    ctrls.AnalogueGain = 1.0
    ctrls.ExposureTime = cam_exposure.get() #microseconds
    picam2.set_controls(ctrls)
    
    cam_starting.set(0)
    cam_running.set(1)

    #### Initialize matplotlib preview display
    im = picam2.capture_image("main")
    imarr = np.array(im)
    
    _, rect1 = getbox(x=roi1_x.get(), y=roi1_y.get(), rad=roi1_rad.get());
    _, rect2 = getbox(x=roi2_x.get(), y=roi2_y.get(), rad=roi2_rad.get());
    
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("Triggered Image Capture with ROI (Do Not Close This Window)")
    imsh = ax.imshow(imarr)
    ax.add_artist(rect1)
    ax.add_artist(rect2)
    plt.draw()
    plt.pause(0.001)
    
    #### Initialize GPIO interrupt
    EXTI_GPIO = 16
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(EXTI_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(EXTI_GPIO, GPIO.RISING, 
        callback=exti_callback, bouncetime=200)
    
    signal.signal(signal.SIGINT, signal_handler) # Catch Ctrl+c for cleanup
    
    trigcnt = 0

    while True:                
        if capture:
            cam_trigcnt.set(trigcnt)
            
            ## CAPTURE A SINGLE IMAGE
            trigcnt_im = trigcnt
            im = picam2.capture_image("main")
            imarr = np.array(im)
            
            # Get rectangles for image extraction
            box1, r1 = getbox(x=roi1_x.get(), y=roi1_y.get(), rad=roi1_rad.get());
            box2, r2 = getbox(x=roi2_x.get(), y=roi2_y.get(), rad=roi2_rad.get());

            im1 = im.crop(box=box1)
            im1_arr = np.array(im1)[:,:,:3] # Note, remove transparency channel here
            avg1 = im1_arr.mean(axis=(0,1))
            avg1 = avg1 - np.array([roi1_bg_r.get(), roi1_bg_g.get(), roi1_bg_b.get()])
            avg1_u8 = np.round(avg1).astype(np.uint8)
            
            datastr1 = "TRIG:{},R:{},G:{},B:{}".format(trigcnt_im,avg1_u8[0],avg1_u8[1],avg1_u8[2])
            roi1_data.set(datastr1)

            im2 = im.crop(box=box2)
            im2_arr = np.array(im2)[:,:,:3] # Note, remove transparency channel here
            avg2 = im2_arr.mean(axis=(0,1))
            avg2 = avg2 - np.array([roi2_bg_r.get(), roi2_bg_g.get(), roi2_bg_b.get()])
            avg2_u8 = np.round(avg2).astype(np.uint8)
            datastr2 = "TRIG:{},R:{},G:{},B:{}".format(trigcnt_im,avg2_u8[0],avg2_u8[1],avg2_u8[2])
            roi2_data.set(datastr2)
            print("ROI1: " + datastr1, "\t" + "ROI2: " + datastr2)
            
            # Update plot data and draw preview plot
            imsh.set_data(imarr)
            #rect1.xy = rect1tmp.xy
            #rect2.xy = rect2tmp.xy
            rect1.set(xy=r1.get_xy(), height=r1.get_height(), width=r1.get_width())
            rect2.set(xy=r2.get_xy(), height=r2.get_height(), width=r2.get_width())
            plt.draw()
            plt.pause(0.001)
    
            capture = False
        elif cam_exposure.get() != exp_us:
            # Adjust exposure time
            ctrls = Controls(picam2)
            exp_us = cam_exposure.get() 
            ctrls.ExposureTime = exp_us #microseconds
            picam2.set_controls(ctrls)
            print("Exposure updated to {} us".format(exp_us))
        else:
            sleep(0.01)
    
    # Finally leave the IOC running with an interactive shell.
    #softioc.interactive_ioc(globals())
    cothread.WaitForQuit()

