# MdxPlatform
# module to send messages to mdx platform middleware

import socket
import json
from collections import OrderedDict

class middlewareClient():
    def __init__(self):
        self.platform_port = 10002
        self.platfrom_buffer_size = 1024
        self.platformSock = None              
        
    # connect to platform middleware
    def connect(self,ip):     
        self.platformSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.platformSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      
        self.platformSock.connect((ip, self.platform_port))        
        #print "Coaster client connecting to middleware at:", ip    
        
        
    def normalize(self, value, scale):
        v = value / scale
        return max(min(1.0, v),-1) # clamp the return value

    def sendXyzrpy(self, units, args):
        msg = encodeXyzrpy(units, args)
        print "sending: ", msg
        self.platformSock.send(msg)
        
    def sendEncodedConfig(self, msg):
        self.platformSock.send(msg)    
        
    #raw {"jsonrpc":"2.0","method":"raw","units":"real","args":[0, 0, 0, 0, 0, 0],"id": null}
    def encodeRaw(self, units, values):
       id = None
       #print units, values  
       data = OrderedDict([("jsonrpc","2.0"),("method","raw"),("units",units),("args",values),("id",id)])
       msg = json.dumps(data, separators=(',',':')) + '\n'
       #print msg
       return msg


    # xyzrpy {"jsonrpc":"2.0","method":"xyzrpy","units":"norm","args":[0, 0, 0, 0, 0, 0],"id": null}
    def encodeXyzrpy(self, units, values):
       id = None
       #print units, values  
       data = OrderedDict([("jsonrpc","2.0"),("method","xyzrpy"),("units",units),("args",values),("id",id)])
       msg = json.dumps(data, separators=(',',':')) + '\n'
       #print msg
       return msg
       
       # config gains {"jsonrpc":"2.0","method":"config","gainX":1,"gainY":1,"gainZ":1,... ,"id": null}
    def encodeGainConfig(self, gainX,gainY,gainZ,gainRoll,gainPitch,gainYaw,gain):
       id = None   
       data = OrderedDict([("jsonrpc","2.0"),("method","config"),("gainX",gainX),("gainY",gainY),("gainZ",gainZ),("gainRoll",gainRoll),("gainPitch",gainPitch),("gainYaw",gainYaw),("gain",gain),("id",id)])
       msg = json.dumps(data, separators=(',',':')) + '\n'
       #print msg
       return msg
       
          # config washout {"jsonrpc":"2.0","method":"config","washoutX":1,"washoutY":1,"washoutZ":1,... ,"id": null}
    def encodeWashoutConfig(self, washoutX,washoutY,washoutZ,washoutRoll,washoutPitch,washoutYaw):
       id = None   
       data = OrderedDict([("jsonrpc","2.0"),("method","config"),("washoutX",washoutX),("washoutY",washoutY),("washoutZ",washoutZ),("washoutRoll",washoutRoll),("washoutPitch",washoutPitch),("washoutYaw",washoutYaw),("id",id)])
       msg = json.dumps(data, separators=(',',':')) + '\n'
       #print msg
       return msg
       
    def sendClientName(self, name):
       data = OrderedDict([("jsonrpc","2.0"),("method","config"),("ClientName",name)])
       msg = json.dumps(data, separators=(',',':')) + '\n'
       self.platformSock.send(msg) 
