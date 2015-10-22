#!/usr/bin/env python
# Python Local NL2 Controller

import socket
import json
from json import encoder
from collections import OrderedDict
from SocketServer import StreamRequestHandler, TCPServer
import SocketServer
import time
import pyautogui
import SendKeys
import msvcrt  # for kbhit

      
def getch():
    return msvcrt.getch().decode('utf-8')                                 

def kbhit():
    # Returns True if keyboard character was hit, False otherwise.
    return msvcrt.kbhit()      


class MyTCPHandler(SocketServer.StreamRequestHandler):
    
    pyautogui.PAUSE = 1
    pyautogui.FAILSAFE = True
    width, height = pyautogui.size()
    print pyautogui.size()

    def pause(self):
        print 'pause'
        pyautogui.click(200, 200)
        time.sleep(0.02)
        #pyautogui.press(['P'])
        SendKeys.SendKeys('P')  
     
    def dispatch(self):
        print 'dispatch'
        pyautogui.click(200, 200)
        time.sleep(0.02)
        #pyautogui.press(['i'])
        SendKeys.SendKeys('i')  
     
    def reset(self):
        print 'reset'
        ##pyautogui.moveTo(width-25, height-25)
        #pyautogui.press(['f4'])
        #pyautogui.click(self.width-25, self.height-20)
        pyautogui.click(1645,895) # for rift
        time.sleep(1.0)
        #pyautogui.press(['f4'])
        
    dispatcher = { 'pause' : pause, 'dispatch' : dispatch,  'reset' : reset} 

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
    HOST, PORT = '', 10007

    # Create the server, binding to localhost on port effector port
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    print "Local NL2 key/mouse controller"
    server.serve_forever()  
   
    