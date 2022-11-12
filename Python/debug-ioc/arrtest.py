#!/bin/python3

import numpy as np

avg1 = np.array([25.1523,205.123123,111.213213])
avg1_u8 = np.round(avg1).astype(np.uint8)
#print("R:{},G:{},B:{}".format(avg1_u8[0],avg1_u8[1],avg1_u8[2]))
print("{},{},{}".format(avg1_u8[0],avg1_u8[1],avg1_u8[2]))


#mystring = "R:25,G:205,B:111"
mystring = "25,205,111"


"TRIG:412302132,R:25,G:205,B:111"
