#!/usr/bin/env python
# Receives button and state messages to control video display

import socket
import json
from json import encoder
from collections import OrderedDict
from SocketServer import StreamRequestHandler, TCPServer
import SocketServer
import time
import msvcrt  # for kbhit
from setConsoleCaption import identifyConsoleApp
import errno

      
def getch():
    return msvcrt.getch().decode('utf-8')                                 

def kbhit():
    # Returns True if keyboard character was hit, False otherwise.
    return msvcrt.kbhit()      


class MyTCPHandler(SocketServer.StreamRequestHandler):
    

    def pause(self):
        print 'pause ', self.state            
     
    def dispatch(self):
        print 'dispatch ', self.state
            
    def reset(self):
        print 'reset ', self.state
    
    def emergencyStop(self):
        print 'emergency stop ', self.state

    def stateChange(self,state):
        self.state = state
        #print state       
               
    dispatcher = { 'pause' : pause, 'dispatch' : dispatch,  'reset' : reset, 'emergencyStop': emergencyStop} 

    def handle(self):    
        while True:   
            if kbhit():
                c = getch()                
                if ord(c) == 27: # ESC
                    sys.exit([0])
            try:             
                json_str = self.rfile.readline().strip()            
                if json_str != None:                          
                    #print "{} wrote:".format(self.client_address[0])
                    try:   
                        j = json.loads(json_str)
                        state = j['state']                   
                        if state != None:
                            self.stateChange(state)                            
                        action = j['action']
                        if action != None:                
                           self.dispatcher[action](self)  
                        else:
                           print 'unable to dispatch', json_str                                   
                    except ValueError:                   
                        pass
            except socket.error as e:
                if e.errno == errno.ECONNREFUSED:
                    print "connection refused"
                if e.errno == errno.WSAECONNRESET:                   
                    print "Connection closed by remote, restart remote controller" 
                    break
                else:
                    print e
                    break
                    


if __name__ == "__main__":
    HOST, PORT = '', 10008
    
    identifyConsoleApp()
    # Create the server, binding to localhost on port effector port
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    print "Remote handler for video control"
    server.serve_forever()  
   
    