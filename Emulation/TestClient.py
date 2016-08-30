# TestClient
# repeatedly sends messages to raise and lower platform
__author__ = 'Michael Margolis'

import MdxPlatformItf
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
platform = MdxPlatformItf.middlewareClient() 


def oscillate(field):
    global dir, interval, step, range, currentPos
    fields = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # platform centered on all axis
    for i in range (0, int(1.0/ step * 4)): # steps the values up and back in + & - directions   
        fields[field] = currentPos # place the stepped value into the list at the given field index
        platform.sendXyzrpy( 'norm', fields) #send the list
        sleep(interval)
        currentPos = currentPos + (dir * step) # one small step for a platform,...
        if currentPos >= 1.0: # reverse direction if at extreme of movement
            dir = -1
        if currentPos <= -1.0:
            dir = 1  
            
def test():      
    platform.connect('localhost') 
 
    while True:
        for f in range(0,6):  
           oscillate(f)
           sleep(.2)
            
if __name__ == "__main__":
   test()        

  
   
    