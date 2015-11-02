# Coaster interface
__author__ = 'Michael Margolis'

import MdxPlatformItf 
import socket
from time import sleep
from struct import *
import collections
from quaternion import Quaternion
from math import pi, degrees
from setConsoleCaption import identifyConsoleApp
import sys
import msvcrt  # for kbhit

interval = .05  #time in seconds between telemetry requests
middleware_ip_addr = 'localhost'

coaster_ip_addr = 'localhost'
coaster_port = 15151
coaster_buffer_size = 1024
BACKLOG = 5 
id=1

N_MSG_GET_VERSION = 3
N_MSG_VERSION = 4
N_MSG_GET_TELEMETRY = 5
N_MSG_TELEMETRY = 6
c_nExtraSizeOffset = 9  # Start of extra size data within message

telemetryMsg = collections.namedtuple('telemetryMsg','state,frame,viewMode,coasterIndex,coasterStyle,train,car,seat,speed,posX,posY,posZ,quatX,quatY,quatZ,quatW,gForceX,gForceY,gForceZ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

platform = MdxPlatformItf.middlewareClient()

def getch():
    return msvcrt.getch().decode('utf-8')                                 

def kbhit():
    # Returns True if keyboard character was hit, False otherwise.
    return msvcrt.kbhit() 
    
def processTelemetryMsg( msg):
   # this version only creates a normalized message
   if(msg.state & 1): # only process if coaster is in play
       if(False):          
           # code here is non-normalized (real) translation and rotation messages
           quat = Quaternion(msg.quatX,msg.quatY,msg.quatZ,msg.quatW)
           pitch = degrees(quat.toPitchFromYUp())
           yaw = degrees(quat.toYawFromYUp())
           roll = degrees(quat.toRollFromYUp())
       else: #normalize          
           quat = Quaternion(msg.quatX,msg.quatY,msg.quatZ,msg.quatW)
           pitch = quat.toPitchFromYUp() / pi
           yaw = quat.toYawFromYUp() / pi
           roll = quat.toRollFromYUp() / pi
           x = platform.normalize(msg.gForceX,1); #second arg is the scale value
           y = platform.normalize(msg.gForceY,1);
           z = platform.normalize(msg.gForceZ,1);
           data = [x,y,z,roll, pitch, yaw] 
           platform.sendXyzrpy('norm', data)           
        
       if( msg.posX != 0 and msg.posY !=0):   
          print msg.posX, msg.posY, msg.posZ, pitch, yaw, roll
          #print "pitch=", degrees( quat.toPitchFromYUp()),quat.toPitchFromYUp(), "roll=" ,degrees(quat.toRollFromYUp()),quat.toRollFromYUp()  
   
# see NL2TelemetryClient.java in NL2 distribution for message format
def createSimpleMessage(requestId, msg):
    result = pack('>cHIHc', 'N',msg,requestId,0,'L')
    return result   

def connectToMiddleware():    
    while True:
        try:
            platform.connect(middleware_ip_addr);
            print "Coaster client connected to Middleware"
            break 
        except socket.error, e:
            print "unable to connect to middleware, retrying: ", middleware_ip_addr
            sleep(.5)
 
 
def connectToCoaster():
     while True:
        try:
           client.connect((coaster_ip_addr, coaster_port))
           print "Coaster client connected to NL2"
           break;
        except socket.error, e:
           print "unable to connect to NL2, retrying: ", coaster_ip_addr
            
def sendName(name):
      try:        
         platform.sendClientName("CoasterClient") #resend name
         print "sent name"
      except :  
          print "Error sending to middleware, attempting reconnect...",          
          try:            
             platform.connect(middleware_ip_addr);            
             sleep(1)              
             platform.sendClientName("CoasterClient") #resend name
             print "reconnected"
          except: 
             #print sys.exc_info()[0]          
             print "unable to message middleware, is it running?"     
                
if __name__ == "__main__":
    print "CoasterClient (press esc followed by q to quit)"
    identifyConsoleApp()
    connectToCoaster()           
    client.send(createSimpleMessage(id, N_MSG_GET_VERSION)) 
    connectToMiddleware() 
    while True:
        try:
            #platform.sendEncodedConfig(platform.encodeWashoutConfig(0.996,0.996,0.996,0.996,0.996,0.996))
            platform.sendClientName("CoasterClient")
            break 
        except socket.error, e:
            print "unable to send config, retrying: ", middleware_ip_addr

    while True:   
        #coastercClient, address = server.accept() 
        if kbhit():
            c = getch()                
            if ord(c) == 27: # ESC
                print "press 'q' to quit, any other key to continue"                       
                if getch() == 'q':
                    sys.exit(0)
                print "CoasterClient running"    
            elif c == ' ': #space
              sendName("CoasterClient") #resend name
                
        data = client.recv(coaster_buffer_size) 
        if data and len(data) >= 10: 
            #print len(data)           
            msg,requestId,size = (unpack('>HIH',data[1:9]))       
            #print msg, requestId, size
            if msg == N_MSG_VERSION:          
                v0,v1,v2,v3 =  unpack('cccc',data[c_nExtraSizeOffset:c_nExtraSizeOffset+4])  
                print 'NL2 version', chr(ord(v0)+48),chr(ord(v1)+48),chr(ord(v2)+48),chr(ord(v3)+48)
                client.send(createSimpleMessage(id, N_MSG_GET_TELEMETRY))
            elif msg == N_MSG_TELEMETRY:           
                if size == 76:
                    t = (unpack('>IIIIIIIIfffffffffff',data[c_nExtraSizeOffset:c_nExtraSizeOffset+76]))
                    tm = telemetryMsg._make(t)                
                    processTelemetryMsg(tm)                    
                else:
                    print 'invalid msg len expected 76, got ', size
                sleep(interval)
                client.send(createSimpleMessage(id, N_MSG_GET_TELEMETRY))
            else:
                print 'unhandled message', msg
            
        

  
   
    