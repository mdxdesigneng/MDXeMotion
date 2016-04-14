# Coaster interface
__author__ = 'Michael Margolis'

import socket
from time import sleep
from struct import *
import collections
from quaternion import Quaternion
from math import pi, degrees
from setConsoleCaption import identifyConsoleApp
import sys
import threading

class CoasterInterface():

    N_MSG_GET_VERSION = 3
    N_MSG_VERSION = 4
    N_MSG_GET_TELEMETRY = 5
    N_MSG_TELEMETRY = 6
    c_nExtraSizeOffset = 9  # Start of extra size data within message
     
    telemetryMsg = collections.namedtuple('telemetryMsg','state,frame,viewMode,coasterIndex,coasterStyle,train,car,seat,speed,posX,posY,posZ,quatX,quatY,quatZ,quatW,gForceX,gForceY,gForceZ')
 
    def __init__(self):
        self.coaster_buffer_size = 1024
        self.coaster_ip_addr = 'localhost'
        self.coaster_port = 15151
        self.interval = .05  #time in seconds between telemetry requests       
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id=1
        
    def run(self, coasterQ):   
        self.connectToCoaster()           
        self.client.send(self.createSimpleMessage(self.id, self.N_MSG_GET_VERSION))   
        self.coaster_msg_q = coasterQ       

        while True:                   
            data = self.client.recv(self.coaster_buffer_size) 
            if data and len(data) >= 10: 
                #print len(data)           
                msg,requestId,size = (unpack('>HIH',data[1:9]))       
                #print msg, requestId, size
                if msg == self.N_MSG_VERSION:          
                    v0,v1,v2,v3 =  unpack('cccc',data[self.c_nExtraSizeOffset:self.c_nExtraSizeOffset+4])  
                    print 'NL2 version', chr(ord(v0)+48),chr(ord(v1)+48),chr(ord(v2)+48),chr(ord(v3)+48)
                    self.client.send(self.createSimpleMessage(self.id, self.N_MSG_GET_TELEMETRY))
                elif msg == self.N_MSG_TELEMETRY:           
                    if size == 76:
                        t = (unpack('>IIIIIIIIfffffffffff',data[self.c_nExtraSizeOffset:self.c_nExtraSizeOffset+76]))
                        tm = self.telemetryMsg._make(t)                
                        self.processTelemetryMsg(tm)                    
                    else:
                        print 'invalid msg len expected 76, got ', size
                    sleep(self.interval)
                    self.client.send(self.createSimpleMessage(self.id, self.N_MSG_GET_TELEMETRY))
                else:
                    print 'unhandled message', msg    
    
    def processTelemetryMsg(self, msg):
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
               x = max(min(1.0, msg.gForceX),-1) # clamp the value 
               y = max(min(1.0, msg.gForceY),-1)             
               z = max(min(1.0, msg.gForceZ),-1)
               data = [x,y,z,roll, pitch, yaw]
               formattedData = [ '%.3f' % elem for elem in data ]                
               self.coaster_msg_q.put(formattedData)                     
            
           ##if( msg.posX != 0 and msg.posY !=0):   
              ##print msg.posX, msg.posY, msg.posZ, pitch, yaw, roll
              #print "pitch=", degrees( quat.toPitchFromYUp()),quat.toPitchFromYUp(), "roll=" ,degrees(quat.toRollFromYUp()),quat.toRollFromYUp()  
       
    # see NL2TelemetryClient.java in NL2 distribution for message format
    def createSimpleMessage(self,requestId, msg):
        result = pack('>cHIHc', 'N',msg,requestId,0,'L')
        return result       
     
    def connectToCoaster(self):
         while True:
            try:
               self.client.connect((self.coaster_ip_addr, self.coaster_port))
               print "Coaster client connected to NL2"              
               break
            except socket.error, e:
               print "unable to connect to NL2, retrying: ", self.coaster_ip_addr                
     
                
if __name__ == "__main__":
    identifyConsoleApp()
    coaster = CoasterInterface()
    coaster_thread = threading.Thread(target=coaster.run)
    coaster_thread.daemon = True
    coaster_thread.start()

    while True:
       if raw_input('\nType quit to stop this script') == 'quit':
         break        
   
        

  
   
    