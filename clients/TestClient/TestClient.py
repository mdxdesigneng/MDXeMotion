# TestClient
# repeatedly sends messages to raise and lower platform
__author__ = 'Michael Margolis'

import MdxPlatformItf as platform
import socket
from time import sleep
from struct import *
import collections
import sys

interval = 0.02 # interval in secs between messages to middleware
period   = 1.0  # time in secs to move from neutral to extremes     
step = 1.0 / (period / interval) # how much to move each interval
currentPos = 0.0;
dir = 1


def oscillate(field):
    global dir, interval, step, range, currentPos
    for i in range (0, int(1.0/ step * 4)):
        fields = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        fields[field] = currentPos
        platform.sendXyzrpy( 'norm', fields)        
        sleep(interval)
        currentPos = currentPos + (dir * step)
        if currentPos >= 1.0-step:
            dir = -1
        if currentPos <= -1.0+step:
            dir = 1 
            
def test():      
    platform.connect('localhost') 
 
    while True:
        for f in range(0,6):  
           oscillate(f)             
            
if __name__ == "__main__":
   test()        

  
   
    