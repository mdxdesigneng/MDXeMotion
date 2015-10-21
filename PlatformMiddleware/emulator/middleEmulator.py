# middleware emulator
# repeatedly sends messages to raise and lower platform

import socket
from time import sleep
import collections
import json
from collections import OrderedDict
import sys

interval = 0.05 # interval in secs between messages to middleware 
minVal = 725
centerVal = 750
maxVal = 775;
step = 5
dir = 1

chair = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chairIP = 'localhost'
chairPort = 10003

try: 
    chair.connect((chairIP, chairPort))  
    print('emulator connected to ' + chairIP)             
except socket.error, e:
    print 'Could not connect to chair' 

geometryMsg = json.dumps(OrderedDict([("jsonrpc","2.0"),("method","geometry")]), separators=(',',':')) + '\n' 
##'{"jsonrpc":"2.0","method":"geometry"}\n'
chair.send(geometryMsg)

fields = [centerVal, centerVal, centerVal, centerVal, centerVal, centerVal]  # platform centered on all axis
dirs = [1,1,1,1,1,1] #  1 increments values, -1 decrements

while True:       
    #print units, values  
    data = OrderedDict([("jsonrpc","2.0"),("method","moveEvent"),("rawArgs",fields)]) # for testing we only form the raw message data
    msg = json.dumps(data, separators=(',',':')) + '\n'
    chair.send(msg)
    print msg
    sleep(interval)
    for i,f in enumerate(fields):      
        f = f + (dirs[i] * step) # one small step for a platform,...
        if f >= maxVal: # reverse direction if at extreme of movement
           dirs[i] = -1
        if f <= minVal:
           dirs[i] = 1              
        fields[i] = f        