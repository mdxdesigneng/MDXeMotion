from Tkinter import *
import socket,errno
import json
import sys
import time
from serial import *
from setConsoleCaption import identifyConsoleApp

serialPort = "COM8"
baudRate = 57600
ser = Serial(serialPort , baudRate, timeout=0, writeTimeout=0) 
serBuffer = ""

# remote control receiver addresses:
#addresses =  ( ('localhost',10007), ('192.168.1.21',10007))
addresses =  ( ('localhost',10007),('localhost',10008))

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
 
class Sender:
    def __init__(self, addr):
        self.addr = addr         
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout = 2
        self.sock.settimeout(self.timeout)
        self.isConnected = False 
        print addr
         
   
    def send(self, msg):                
         if self.sock:
            if not self.isConnected:
               self.connect()
            if self.isConnected:
               try:
                   self.sock.sendall(msg)
                   print "Sending ",msg[:-1], ' to ', self.addr                                 
               except socket.error as e:
                   if e.errno == errno.ECONNREFUSED:
                       print 'Could not connect to remote: ',
                       print self.addr 
                   else:                   
                       print e                 
                   
    def connect(self):
       try:                     
            self.sock.connect(self.addr)           
            print('Remote controller connected to ', self.addr)
            self.isConnected = True                                     
       except socket.error as e:   
           if e.errno == errno.ECONNREFUSED:
               print 'Could not connect to remote: ',
               print self.addr 
           else:                   
               print e  
    
    def quit(self, quitMsg):
        self.send(quitMsg)
        self.sock.shutdown(socket.SHUT_RDWR)
        time.sleep(self.timeout + 1)
        self.sock.close()

    
class RemoteController:
    def __init__(self, master, addresses):
        self.senders = [] 
        for adr in addresses:          
           self.senders.append( Sender(adr)) 
        
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
        
        self.close_button = Button(master, text="quit", command=self.quit)
        self.close_button.pack(side = BOTTOM, padx=8)
              
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
        print("Dispatch")
        self.sendMsg('{"action":"dispatch"',self.state)           
     
    
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
        print("Reset") 
        self.sendMsg('{"action":"reset"',self.state)
  
        
    def emergencyStop(self):
        if self.isPaused:
            print "Already paused"
        else:
            self.pause()
            self.state = 'Emergency stopped'
            print("Emergency Stop")
            self.sendMsg('{"action":"emergencyStop"',self.state)
           # msg = '{"action":"emergencyStop","state":self.state}\n'
            #sock1.sendall(msg)   
        
    
    def sendMsg(self, buttonStr, state):        
         msg = buttonStr + ',"state":"' + state +'"}\n' 
         for s in self.senders:
            s.send(msg)
         print("\n")   
    
    def quit(self):  
       msg = '{"action":"quit"}'
       for s in self.senders:
           s.quit(msg)         
       self.master.quit 

     
if __name__ == "__main__": 
    identifyConsoleApp()
    print "NL2 key/mouse remote controller"   
    root = Tk()
    controller = RemoteController(root, addresses) 
    root.after(20, pollSerial) 
    root.mainloop()
