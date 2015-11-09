#!/usr/bin/env python
# Python Local NL2 Controller

import socket
import json
from json import encoder
from collections import OrderedDict
from SocketServer import StreamRequestHandler, TCPServer
import SocketServer
import time
import win32gui, win32api, win32con, ctypes
import msvcrt  # for kbhit
from Mouse import Mouse
from setConsoleCaption import identifyConsoleApp

mouse = Mouse()      

def getch():
    return msvcrt.getch().decode('utf-8')                                 

def kbhit():
    # Returns True if keyboard character was hit, False otherwise.
    return msvcrt.kbhit()      

resetPoint = (1440,840)    
 
def testReset():
    print 'Moving cursor to reset point'    
    mouse.visible_click_rel( windowHandle,resetPoint)        
    

class MyTCPHandler(SocketServer.StreamRequestHandler):   
    
    def sendKey(self, c):
        # not used in this version
        win32api.SendMessage(windowHandle, win32con.WM_KEYDOWN, ord(c), 0) 
        win32api.SendMessage(windowHandle, win32con.WM_CHAR, ord(c), 0)  
        win32api.SendMessage(windowHandle, win32con.WM_KEYUP, ord(c), 0)           
        
        
    def pause(self):
        print 'pause'     
        #self.sendKey('P')
        scancode = 0x19
        lparam =  1 + (scancode << 16)    
        global windowHandle
        win32api.SendMessage(windowHandle, win32con.WM_KEYDOWN, ord('P'), lparam) 
        win32api.SendMessage(windowHandle, win32con.WM_CHAR, ord('P'), lparam)  
        win32api.SendMessage(windowHandle, win32con.WM_KEYUP, ord('P'), lparam)          
     
    def dispatch(self):
        print 'dispatch'
        #self.sendKey('i') 
        scancode = 0x17
        lparam =  1 + (scancode << 16)     
        global windowHandle
        win32api.SendMessage(windowHandle, win32con.WM_KEYDOWN, ord('I'), lparam) 
        win32api.SendMessage(windowHandle, win32con.WM_CHAR, ord('i'), lparam)  
        win32api.SendMessage(windowHandle, win32con.WM_KEYUP, ord('I'), lparam)  
  
        self.isCursorVisible = False 
  
    def emergencyStop(self):
        print 'emergency stop '        
  
     
    def reset(self):
        print 'reset'
        global resetPoint
        global windowHandle
        global mouse
        
        if self.isCursorVisible:
           testReset()
        else:
           mouse.invisible_click_rel( windowHandle,resetPoint)        
           time.sleep(0.5)
           mouse.invisible_click_rel( windowHandle,(300,300)) # move mouse to remove reset tool tip        
        
    dispatcher = { 'pause' : pause, 'dispatch' : dispatch,  'reset' : reset, 'emergencyStop': emergencyStop}  
    isCursorVisible = True  #this is set to False after first dispatch message    
  
    
    def handle(self):    
      
        while True:   
            if kbhit():
                c = getch()                
                if ord(c) == 27: # ESC
                    sys.exit([0])
                         
            json_str = self.rfile.readline().strip()
            if json_str != None:                          
                #print "{} wrote:".format(self.client_address[0])               
                j = json.loads(json_str)              
                action = j['action']
                if action != None:                
                   self.dispatcher[action](self)  
                else:
                   print  json_str           
  

if __name__ == "__main__":   
    identifyConsoleApp()
    print "Local NL2 key/mouse controller"  
    print "Restart remote controller if that was already running" 
    print "Press reset to show mouse cursor point to reset ride"   
    windowClass = "NL3D_MAIN_{7F825CE1-21E4-4C1B-B657-DE6FCD9AEB12}"
    windowname = "Colossus.nl2park (ReadOnly) - NoLimits 2"   
    windowHandle = win32gui.FindWindow(windowClass,None );
    if windowHandle > 0:
       print "found NL2 window at ", windowHandle
       testReset()  # move the mouse to the reset location in the NL2 window
       print "Ready for connection from remote controller"  
       # Create the server, binding to localhost on port effector port
       HOST, PORT = '', 10007 
       server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
       server.serve_forever()
    else:
      print "Did not find NL2 window, startup NL2 and rerun this script" 
  
   
    