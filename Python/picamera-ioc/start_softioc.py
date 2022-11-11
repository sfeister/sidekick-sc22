# Import the basic framework components.
from softioc import softioc, builder
import cothread
from PIL_based_img_process import *
from epic_cam import *
import logging
import time

logging.basicConfig(level=logging.DEBUG)

# Set the record prefix
builder.SetDeviceName("DEMO")

# Create some records
ai = builder.aIn('GET_COLOR', initial_value=5)
a5 = builder.aIn('A9', initial_value=7)
ao = builder.aOut('COLOR_DETECT', initial_value=12, always_update=True,
                  on_update=lambda v: call_color_detect(v))
ao = builder.aOut('SNAP', initial_value=0, always_update=True,
                  on_update=lambda v: take_snapshot(v))
astart = builder.aOut('CAM_ON', initial_value=0, always_update=True,
                  on_update=lambda v: start_camera(v))
astop = builder.aOut('CAM_OFF', initial_value=0, always_update=True,
                  on_update=lambda v: stop_camera(v))


# Boilerplate get the IOC started
builder.LoadDatabase()
softioc.iocInit()

# Start processes required to be run after iocInit
ecam = epic_camera()
def display():
    print("display enter")
    ecam.start()
    print("display exit")

def take_snapshot(v):
    ecam.take_snapshot()

def call_color_detect(v):
    ret = run_color_detection()
    ai.set(ret)

def start_camera(v):
    print("start_camera enter")
    #cothread.Spawn(display)
    display()
    print("start_camera exit")
   
def stop_camera(v):
    ecam.stop()

#cothread.Spawn(keep_running)

# Finally leave the IOC running with an interactive shell.
#softioc.interactive_ioc(globals())
cothread.WaitForQuit()
