#!/bin/python3

from softioc import softioc, builder
import cothread
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Set the record prefix
    builder.SetDeviceName("CAM")

    ## Create some records

    # Run contols
    cam_enable = builder.boolOut("ENABLE", ZNAM="false", ONAM="true")
    debug_enable = builder.boolOut("DEBUG:ENABLE", ZNAM="false", ONAM="true")

    # Run status
    cam_starting = builder.boolIn("STARTING", ZNAM="false", ONAM="true")
    cam_running = builder.boolIn("RUNNING", ZNAM="false", ONAM="true")
    cam_stopping = builder.boolIn("STOPPING", ZNAM="false", ONAM="true")

        # Format e.g. "TRIG:412302132,R:25,G:205,B:111"
    roi1_data = builder.stringIn("ROI1:DATA", initial_value="")
    roi1_x = builder.longOut("ROI1:X", initial_value=100)
    roi1_y = builder.longOut("ROI1:Y", initial_value=100)
    roi1_rad = builder.longOut("ROI1:RAD", initial_value=10)

    roi2_data = builder.stringIn("ROI2:DATA", initial_value="")
    roi2_x = builder.longOut("ROI2:X", initial_value=100)
    roi2_y = builder.longOut("ROI2:Y", initial_value=100)
    roi2_rad = builder.longOut("ROI2:RAD", initial_value=10)

    # Boilerplate get the IOC started
    builder.LoadDatabase()
    softioc.iocInit()
    
    # Finally leave the IOC running with an interactive shell.
    #softioc.interactive_ioc(globals())
    cothread.WaitForQuit()

