# MdxPlatform
# module to send messages to mdx platform middleware

import socket
import json
from collections import OrderedDict

platform_port = 10002
platfrom_buffer_size = 1024

platformSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to platform middleware
def connect(ip):
    platformSock.connect((ip, platform_port))
    #print "Coaster client connecting to middleware at:", ip    
    
def disconnect():
    print "disconnected"
    
def normalize(value, scale):
    v = value / scale
    return max(min(1.0, v),-1) # clamp the return value

def sendXyzrpy(units, args):
    msg = encodeXyzrpy(units, args)
    print "sending: ", msg
    platformSock.send(msg)
    
def sendEncodedConfig(msg):
    platformSock.send(msg)    
    
#raw {"jsonrpc":"2.0","method":"raw","units":"real","args":[0, 0, 0, 0, 0, 0],"id": null}
def encodeRaw( units, values):
   id = None
   #print units, values  
   data = OrderedDict([("jsonrpc","2.0"),("method","raw"),("units",units),("args",values),("id",id)])
   msg = json.dumps(data, separators=(',',':')) + '\n'
   #print msg
   return msg


# xyzrpy {"jsonrpc":"2.0","method":"xyzrpy","units":"norm","args":[0, 0, 0, 0, 0, 0],"id": null}
def encodeXyzrpy( units, values):
   id = None
   #print units, values  
   data = OrderedDict([("jsonrpc","2.0"),("method","xyzrpy"),("units",units),("args",values),("id",id)])
   msg = json.dumps(data, separators=(',',':')) + '\n'
   #print msg
   return msg
   
   # config gains {"jsonrpc":"2.0","method":"config","gainX":1,"gainY":1,"gainZ":1,... ,"id": null}
def encodeGainConfig(gainX,gainY,gainZ,gainRoll,gainPitch,gainYaw,gain):
   id = None   
   data = OrderedDict([("jsonrpc","2.0"),("method","config"),("gainX",gainX),("gainY",gainY),("gainZ",gainZ),("gainRoll",gainRoll),("gainPitch",gainPitch),("gainYaw",gainYaw),("gain",gain),("id",id)])
   msg = json.dumps(data, separators=(',',':')) + '\n'
   #print msg
   return msg
   
      # config washout {"jsonrpc":"2.0","method":"config","washoutX":1,"washoutY":1,"washoutZ":1,... ,"id": null}
def encodeWashoutConfig(washoutX,washoutY,washoutZ,washoutRoll,washoutPitch,washoutYaw):
   id = None   
   data = OrderedDict([("jsonrpc","2.0"),("method","config"),("washoutX",washoutX),("washoutY",washoutY),("washoutZ",washoutZ),("washoutRoll",washoutRoll),("washoutPitch",washoutPitch),("washoutYaw",washoutYaw),("id",id)])
   msg = json.dumps(data, separators=(',',':')) + '\n'
   #print msg
   return msg
