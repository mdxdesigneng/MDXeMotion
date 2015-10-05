# Flightgear interface
__author__ = 'Michael Margolis'

import MdxPlatformItf as itf
import socket
from time import sleep
from struct import *
import collections

fg_ip_addr = 'localhost'
fg_port = 5500
fg_buffer_size = 1024

#factors to convert real world angles to normalized values
PITCH_SCALE_FACTOR = 180.0  
ROLL_SCALE_FACTOR = 180.0
YAW_SCALE_FACTOR = 180.0
    
# flightgear telemetry messages are of the form: '~pitch=28,roll=40,yaw=0,Az=1,heading=318,alt=34,engRPM=0,velocity=0'   
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # flightgear telemetry uses UDP messages
client.bind((fg_ip_addr, fg_port)) # bind to the Flightgear port

itf.connect('localhost'); # connect to middleware

print "Starting"
minp = 0.0
maxp=0.0
minr = 0.0
maxr=0.0
miny = 0.0
maxy=0.0

while True:      
    data = client.recv(fg_buffer_size)   
    if data[0] == '{':
        print 'Flightgear telemetry starting' 
    elif data[0] == '}':
        print 'Flightgear telemetry ending' 
    else:  
        mydict = dict(item.split("=") for item in data.split(","))
        #print data
        print mydict['~pitch'],  mydict['roll'],  mydict['yaw']              
        roll  = itf.normalize(float(mydict['roll']), ROLL_SCALE_FACTOR)
        pitch = itf.normalize(float(mydict['~pitch']), PITCH_SCALE_FACTOR)
        yaw   = itf.normalize(float(mydict['yaw']) ,YAW_SCALE_FACTOR)
        msg = [0,0,0,roll, pitch, yaw]
            
        #print msg
        itf.sendXyzrpy('norm', msg)         

            
        

  
   
    