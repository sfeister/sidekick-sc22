#!/bin/python3

from picamera2 import Picamera2, Preview
import time
from PIL import Image
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from softioc import softioc, builder
import cothread

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
    builder.SetDeviceName("CAM")

    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration()
    picam2.configure(camera_config)
    picam2.start()

    im = picam2.capture_image("main")
    imarr = np.array(im)
    #imarr = picam2.capture_array("main")

    # Hard code positions of rectangles here!
    box1, rect1 = getbox(x=299, y=387, rad=10);
    box2, rect2 = getbox(x=1081, y=392, rad=10);

    im1 = im.crop(box=box1)
    im1_arr = np.array(im1)[:,:,:3] # Note, remove transparency channel here
    avg1 = im1_arr.mean(axis=(0,1))
    avg1_u8 = np.round(avg1).astype(np.uint8)

    im2 = im.crop(box=box2)
    im2_arr = np.array(im2)[:,:,:3] # Note, remove transparency channel here
    avg2 = im2_arr.mean(axis=(0,1))
    avg2_u8 = np.round(avg2).astype(np.uint8)

    print(avg1_u8)
    print(avg2_u8)

    debug = True;
    if debug:
        im1.show()
        im2.show()

        fig, ax = plt.subplots()
        ax.imshow(imarr)
        ax.add_patch(rect1)
        ax.add_patch(rect2)

        plt.show()


