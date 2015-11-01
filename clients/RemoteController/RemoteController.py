from Tkinter import *
import socket
import json
import sys
import time
from serial import *
from setConsoleCaption import identifyConsoleApp

serialPort = "COM25"
baudRate = 9600
ser = Serial(serialPort , baudRate, timeout=0, writeTimeout=0) 
serBuffer = ""

ip1 = 'localhost'
ip2 = '' #'192.168.1.21'
remote_port = 10007
buffer_size = 64   
   
states = { "ready" : 0, "running" : 1,  "paused" : 2, "stopped" : 3} 
  
def pollSerial():
       
    while True:   
      c = ser.read()
      if len(c) == 0:
          break    
      global serBuffer    
      if c == '\n':
         if len(serBuffer) > 0:
              controller.doAction(serBuffer)  
              serBuffer = ''
      elif c >= ' ': # ignore controle chars
        serBuffer += c
    state = states[controller.getState()]
    ser.write(state)     
    root.after(20, pollSerial) 
        
class RemoteController:
    def __init__(self, master):
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.actions = { 'pause' : self.pause, 'dispatch' : self.dispatch,  'reset' : self.reset, 'emergencyStop' : self.emergencyStop} 
        self.state = 'ready'
        
        frame = Frame(master)
        frame.pack()       
             
        self.master = master
        self.master.title("NL2 Controller")

        self.label = Label(master, text="No Limits Remote Controller")
        self.label.pack()

        self.dispatch_button = Button(master, text="Dispatch", command=self.dispatch)
        self.dispatch_button.pack(side = LEFT,padx=(8,4))
        
        self.pause_button = Button(master, text="Pause", command=self.pause)
        self.pause_button.pack(side = LEFT,padx=(8,4))
        
        self.reset_button = Button(master, text="Reset", command=self.reset)
        self.reset_button.pack(side = LEFT,padx=(8,4))          
        
        self.reset_button = Button(master, text="EmergencyStop", command=self.emergencyStop)
        self.reset_button.pack(side = LEFT,padx=(8,4))   
        
        self.close_button = Button(master, text="Close", command=self.quit)
        self.close_button.pack(side = BOTTOM, padx=8)
        
        self.connect()
        self.isPaused = False
     
    def getState(self):  
        return self.state
        
    def doAction(self,msg): 
         action = self.actions[msg]
         if action:
             action()  
         else:
            print msg
            
           
    def dispatch(self):
        if self.isPaused:
            self.pause() # turn pause off before dispatch
        self.state = 'running'
        self.sendMsg('{"action":"dispatch"',self.state)           
        print("Dispatch")
    
    def pause(self):
        if self.isPaused: 
            self.isPaused = False            
            print("Pause off")
            self.state = 'running'
        else:           
            self.isPaused = True            
            print("Pause")
            self.state = 'paused'
        self.sendMsg('{"action":"pause"', self.state)                     
        
    def reset(self):
        if self.isPaused:           
            self.pause() # turn pause off before reset           
        self.state = 'ready'
        self.sendMsg('{"action":"reset"',self.state)
        print("Reset") 
        
    def emergencyStop(self):
        if self.isPaused:
            print "Already paused"
        else:
            self.pause()
            self.state = 'stopped'
            self.sendMsg('{"action":"emergencyStop"',self.state)
           # msg = '{"action":"emergencyStop","state":self.state}\n'
            #sock1.sendall(msg)   
            print("Emergency Stop")
    
    def sendMsg(self, buttonStr, state):        
         msg = buttonStr + ',"state":"' + state +'"}\n' 
         if self.sock1:           
            self.sock1.sendall(msg)             
         if self.sock2:          
            self.sock2.sendall(msg)          
        
    def connect(self):
       try: 
           if len(ip1) > 0: 
               self.sock1.connect((ip1, remote_port))  
               print('Remote controller connected to ' + ip1)  
           else:
               self.sock1 = None
           if len(ip2) > 0: 
               self.sock2.connect((ip2, remote_port))  
               print('Remote controller connected to ' + ip2)
           else:
               self.sock2 = None               
       except socket.error, e:
           print 'Could not connect to server %s' % ip1, e 
       time.sleep(2.0)    
    
    def quit(self):
       try: 
           if self.sock1:    
               self.sock1.close()       
           if self.sock2:              
               self.sock2.close()                  
       except socket.error, e:
           print 'error closing socket ' , e 
       self.master.quit 
    
if __name__ == "__main__": 
    identifyConsoleApp()
    print "NL2 key/mouse remote controller"    
    print "Run this after starting local controllers"     
    args = (sys.argv)
    if len(args) > 1 :   
       print args
       ip1 = args[1]
       if len(args) > 2 : 
           ip2 = args[2]
       
    print ip1
    root = Tk()
    controller = RemoteController(root) 
    root.after(20, pollSerial) 
    root.mainloop()