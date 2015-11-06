#!/usr/bin/env python
# Python Coaster client

import json
from json import encoder
import socket
import SocketServer
import threading
import sys 
from Queue import Queue
import win32gui, win32api, win32con, ctypes
from Mouse import Mouse
import time
from CoasterInterface import CoasterInterface
import MdxPlatformItf 

remote_msg_q = Queue()
coaster_msg_q = Queue()

class remoteActions():
    mouse = Mouse()
    resetPoint = (1440,840)
    queue = None

    def __init__(self): 
       #print "remote action thread is: ", threading.currentThread().getName()    
       windowClass = "NL3D_MAIN_{7F825CE1-21E4-4C1B-B657-DE6FCD9AEB12}"
       windowname = "Colossus.nl2park (ReadOnly) - NoLimits 2"
       self.hwnd = win32gui.FindWindow(windowClass,None );
       self.isCursorVisible = True  #this is set to False after first dispatch message 

    def isReady(self):
        #print "NL2 window is ", self.hwnd  
        return self.hwnd != None

    def testReset(self):
       print 'Moving cursor to reset point'
       self.mouse.visible_click_rel( self.hwnd, self.resetPoint)

    def sendKey(self, c):
        # not used in this version
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, ord(c), 0) 
        win32api.SendMessage(self.hwnd, win32con.WM_CHAR, ord(c), 0)  
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, ord(c), 0)


    def pause(self):
        print 'pause' 
        #self.sendKey('P')
        scancode = 0x19
        lparam =  1 + (scancode << 16)
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, ord('P'), lparam) 
        win32api.SendMessage(self.hwnd, win32con.WM_CHAR, ord('P'), lparam)  
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, ord('P'), lparam)  
 
    def dispatch(self):
        print 'dispatch'
        #self.sendKey('i') 
        scancode = 0x17
        lparam =  1 + (scancode << 16)  
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, ord('I'), lparam) 
        win32api.SendMessage(self.hwnd, win32con.WM_CHAR, ord('i'), lparam)  
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, ord('I'), lparam)

        self.isCursorVisible = False 

    def openHarness(self):
        print 'Closing Harness'
        scancode = 0x48
        lparam =  1 + (scancode << 16)  
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, ord('8'), lparam) 
        win32api.SendMessage(self.hwnd, win32con.WM_CHAR, ord('8'), lparam)  
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, ord('8'), lparam)


    def closeHarness(self):
        print 'Closing Harness'
        scancode = 0x50
        lparam =  1 + (scancode << 16)  
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, ord('2'), lparam) 
        win32api.SendMessage(self.hwnd, win32con.WM_CHAR, ord('2'), lparam)  
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, ord('2'), lparam)

    def emergencyStop(self):
        print 'emergency stop '
  
 
    def reset(self):
        print 'reset' 
        if self.isCursorVisible:
           self.testReset()
        else:
           self.mouse.invisible_click_rel( self.hwnd, self.resetPoint)
           time.sleep(0.5)
           self.mouse.invisible_click_rel( self.hwnd,(300,300)) # move mouse to remove reset tool tip

class RemoteTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):     
       #print "queue in handle is",self.queue
       print "Local NL2 key/mouse controller is active" 
       print "Press reset to show mouse cursor point to reset ride"
      
       global remote_msg_q
       self.queue = remote_msg_q           
       while True: 
            #print "remote thread : ", threading.currentThread().getName()
            try:
                json_str = self.rfile.readline().strip()              
                if json_str != None:                    
                    j = json.loads(json_str)
                    action = j['action']
                    if action != None: 
                       if action =='quit':
                          print 'type quit to exit'
                          break
                       else:
                          self.queue.put(action)
                          #print "in handler, action=", action, self.queue
                    else:
                       print  json_str
            except socket.timeout:
                continue                       
            except socket.error:
                print "Remote control connection error, try (re)starting the remote controller"
                while True:
                    try:
                       self.rfile.readline().strip() 
                       # todo - the first remote command after reconnect is ignored
                       break
                    #todo - exit if keyboard interrupt?
                    except socket.error:
                        pass  

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass 

class Client():
   def __init__(self):          
       self.middleware_ip_addr = 'localhost'
       self.platform = MdxPlatformItf.middlewareClient() 
      
   def run(self, coasterQ, remoteQ): 
        #print "client run thread is: ", threading.currentThread().getName()
        self.coasterQ = coasterQ
        self.remoteQ = remoteQ
        self.connectToMiddleware()
        self.do = remoteActions()          
        #print "coaster queue=",coasterQ, "remote queue=", remoteQ 
   
        while True:
            try:
                #platform.sendEncodedConfig(platform.encodeWashoutConfig(0.996,0.996,0.996,0.996,0.996,0.996))
                self.platform.sendClientName("CoasterClient")
                break 
            except socket.error, e:
                print "unable to send config, retrying: ", self.middleware_ip_addr 
  
        if self.do.isReady(): 
            self.do.testReset()  # move the mouse to the reset location in the NL2 window
            print "ready to receive remote commands (restart remote controller if that was already running)" 
            while True:   
               #print "client run thread: ", threading.currentThread().getName()           
               while not self.coasterQ.empty():
                  data = self.coasterQ.get(False)                
                  self.platform.sendXyzrpy('norm', data)                   
               while not self.remoteQ.empty(): 
                  action = self.remoteQ.get(False)
                  #print "got remote action",action, self.remoteQ 
                  if action == 'pause':
                      self.do.pause()
                  elif action == 'dispatch':
                      self.do.closeHarness()
                      self.platform.sendActivate(True)
                      time.sleep(2)
                      self.do.dispatch()
                  elif action == 'reset':
                      self.do.reset()
                      self.do.openHarness()
                      self.platform.sendActivate(False)  
                  elif action == 'emergencyStop':
                      self.do.emergencyStop()                 
        else:
           print "is NL2 running?" 

       
   def connectToMiddleware(self):
        while True:
            try:
                self.platform.connect(self.middleware_ip_addr);
                print "Coaster client connected to Middleware"
                break 
            except socket.error, e:
                print "unable to connect to middleware, retrying: ", self.middleware_ip_addr
                time.sleep(.5)
   def sendName(self,name):
          try:
             self.platform.sendClientName("CoasterClient") #resend name
             print "sent name"
          except :  
              print "Error sending to middleware, attempting reconnect...",  
              try:
                 self.platform.connect(self.middleware_ip_addr);
                 sleep(1)  
                 self.platform.sendClientName("CoasterClient") #resend name
                 print "reconnected"
              except: 
                 #print sys.exc_info()[0]  
                 print "unable to message middleware, is it running?"

if __name__ == "__main__":   
    HOST, PORT = "localhost", 10007  
    server = ThreadedTCPServer((HOST, PORT), RemoteTCPHandler)
    remote_server_thread = threading.Thread(target=server.serve_forever)
    remote_server_thread.daemon = True
    remote_server_thread.start() 

    coaster = CoasterInterface()
    coaster_thread = threading.Thread(target=coaster.run, args=(coaster_msg_q,))
    coaster_thread.daemon = True
    coaster_thread.start()
    time.sleep(1) #cosmetic to control order of console info

    platformClient = Client()
    client_thread = threading.Thread(target=platformClient.run, args=(coaster_msg_q, remote_msg_q,))
    client_thread.daemon = True
    client_thread.start()
   
    time.sleep(1.5)      
    while True:  
        if raw_input("type quit to stop this script\n") == 'quit': 
            break;
            
    server.shutdown() 
    print "exiting"
    time.sleep(1)
