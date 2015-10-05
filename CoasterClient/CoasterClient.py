# Coaster interface
__author__ = 'Michael Margolis'

import MdxPlatformItf
import socket
from time import sleep
from struct import *
import collections
from quaternion import Quaternion
from math import pi, degrees

coaster_ip_addr = 'localhost'
coaster_port = 15151
coaster_buffer_size = 1024
BACKLOG = 5 
id=1

COASTER_PITCH_SCALE_FACTOR = 80
COASTER_ROLL_SCALE_FACTOR = 80
COASTER_YAW_SCALE_FACTOR = 180

N_MSG_GET_VERSION = 3
N_MSG_VERSION = 4
N_MSG_GET_TELEMETRY = 5
N_MSG_TELEMETRY = 6
c_nExtraSizeOffset = 9  # Start of extra size data within message

telemetryMsg = collections.namedtuple('telemetryMsg','state,frame,viewMode,coasterIndex,coasterStyle,train,car,seat,speed,posX,posY,posZ,quatX,quatY,quatZ,quatW,gForceX,gForceY,gForceZ')

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
           data = [0,0,msg.gForceZ,roll, pitch, yaw] 
           MdxPlatformItf.sendXyzrpy('norm', data) 
        
       if( msg.posX != 0 and msg.posY !=0):   
          print msg.posX, msg.posY, msg.posZ, pitch, yaw, roll
          #print "pitch=", degrees( quat.toPitchFromYUp()),quat.toPitchFromYUp(), "roll=" ,degrees(quat.toRollFromYUp()),quat.toRollFromYUp()
   
# see NL2TelemetryClient.java in NL2 distribution for message format
def createSimpleMessage(requestId, msg):
    result = pack('>cHIHc', 'N',msg,requestId,0,'L')
    return result    

    
MdxPlatformItf.connect('localhost');
#test messages
#MdxPlatformItf.sendXyzrpy( 'norm', [0,0,0,.25,.1,-.1]) 
#MdxPlatformItf.sendXyzrpy( 'norm', [0,0,0,-.25,.1,.1]) 
    
#MdxPlatformItf.encodeRaw( 'real', [1.0,2,3,4,5,6])    
#MdxPlatformItf.encodeXyzrpy( 'norm', [1,2.0,3,4,5,6])   
 
#MdxPlatformItf.sendEncodedConfig(MdxPlatformItf.encodeGainConfig(1,1,1,0.8,0.7,0.6,1.0))
#MdxPlatformItf.sendEncodedConfig(MdxPlatformItf.encodeWashoutConfig(1,1,0.996,0.996,0.996,0.996))
   
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((coaster_ip_addr, coaster_port))
client.send(createSimpleMessage(id, N_MSG_GET_VERSION))

while True:   
    #coastercClient, address = server.accept() 
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
            sleep(0.02)
            client.send(createSimpleMessage(id, N_MSG_GET_TELEMETRY))
        else:
            print 'unhandled message', msg
            
        

  
   
    