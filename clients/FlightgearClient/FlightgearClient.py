# Flightgear interface
__author__ = 'Michael Margolis'

import MdxPlatformItf
import socket
from time import sleep
from struct import *
import collections
from setConsoleCaption import identifyConsoleApp
import msvcrt  # for kbhit

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

middleware_ip_addr = 'localhost'
platform = MdxPlatformItf.middlewareClient()

def getch():
    return msvcrt.getch().decode('utf-8')                                 

def kbhit():
    # Returns True if keyboard character was hit, False otherwise.
    return msvcrt.kbhit() 

def connectToMiddleware():    
    while True:
        try:
            platform.connect(middleware_ip_addr);
            print "Flightgear client connected to Middleware"
            break 
        except socket.error, e:
            print "unable to connect to middleware, retrying: ", middleware_ip_addr
            sleep(.5)
            
if __name__ == "__main__":
    print "Flightgear Client"
    identifyConsoleApp()    
    connectToMiddleware()    
    minp = 0.0
    maxp=0.0
    minr = 0.0
    maxr=0.0
    miny = 0.0
    maxy=0.0
    
    while True:      
        while True:
            try:
                #platform.sendEncodedConfig(platform.encodeWashoutConfig(0.996,0.996,0.996,0.996,0.996,0.996))
                platform.sendClientName("FlightgearClient")
                break 
            except socket.error, e:
                print "unable to send config, retrying: ", middleware_ip_addr
        
        if kbhit():
            c = getch()                
            if ord(c) == 27: # ESC
                print "press 'q' to quit, any other key to continue"                       
                if getch() == 'q':
                    sys.exit(0)
                print "FlightgearClient running"    
            elif c == ' ': #space
              sendName("FlightgearClient") #resend name
    
        data = client.recv(fg_buffer_size)   
        if data[0] == '{':
            print 'Flightgear telemetry starting' 
        elif data[0] == '}':
            print 'Flightgear telemetry ending' 
        else:  
            mydict = dict(item.split("=") for item in data.split(","))
            #print data
            print mydict['~pitch'],  mydict['roll'],  mydict['yaw']              
            roll  = platform.normalize(float(mydict['roll']), ROLL_SCALE_FACTOR)
            pitch = platform.normalize(float(mydict['~pitch']), PITCH_SCALE_FACTOR)
            yaw   = platform.normalize(float(mydict['yaw']) ,YAW_SCALE_FACTOR)
            msg = [0,0,0,roll, pitch, yaw]
                
            #print msg
            platform.sendXyzrpy('norm', msg)         

            
        

  
   
    