from Tkinter import *
import socket
import json
import sys
import time
from serial import *

serialPort = "COM25"
baudRate = 9600
ser = Serial(serialPort , baudRate, timeout=0, writeTimeout=0) 
serBuffer = ""

sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip1 = 'localhost'
ip2 = '' #'192.168.1.21'
remote_port = 10006
buffer_size = 64   
   
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
    root.after(20, pollSerial) 
        
class RemoteController:
    def __init__(self, master):
        self.actions = { 'pause' : self.pause, 'dispatch' : self.dispatch,  'reset' : self.reset} 
        
        frame = Frame(master)
        frame.pack()       
             
        self.master = master
        master.title("NL2 Controller")

        self.label = Label(master, text="No Limits Remote Controller")
        self.label.pack()

        self.dispatch_button = Button(master, text="Dispatch", command=self.dispatch)
        self.dispatch_button.pack(side = LEFT,padx=(8,4))
        
        self.pause_button = Button(master, text="Pause", command=self.pause)
        self.pause_button.pack(side = LEFT,padx=(8,4))
        
        self.reset_button = Button(master, text="Reset", command=self.reset)
        self.reset_button.pack(side = LEFT,padx=(8,4))          
        
        self.close_button = Button(master, text="Close", command=self.quit)
        self.close_button.pack(side = BOTTOM, padx=8)
        
        self.connect()
     
    def doAction(self,msg): 
         action = self.actions[msg]
         if action:
             action()  
         else:
            print msg
            
           
    def dispatch(self):
        msg = '{"action":"dispatch"}\n'        
        sock1.sendall(msg)   
        print("Dispatch")
    
    def pause(self):
        msg = '{"action":"pause"}\n'        
        sock1.sendall(msg)   
        print("Pause")
        
    def reset(self):
        msg = '{"action":"reset"}\n'        
        sock1.sendall(msg)   
        print("Reset") 
        
    def connect(self):
       try: 
           if len(ip1) > 0: 
               sock1.connect((ip1, remote_port))  
               print('Remote controller connected to ' + ip1)  
           if len(ip2) > 0: 
               sock2.connect((ip2, remote_port))  
               print('Remote controller connected to ' + ip2)                
       except socket.error, e:
           print 'Could not connect to server %s' % ip1 
       time.sleep(2.0)    
    
    def quit(self):
       try: 
           if sock1: 
               sock1.close()       
           if sock2: 
               sock2.close()                  
       except socket.error, e:
           print 'error closing socket ' , e 
       master.quit 
    
    


print "NL2 key/mouse remote controller"    
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