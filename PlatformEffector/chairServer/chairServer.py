# Chair Server

import socket
import json
import SocketServer
import sys


_in =[790 ,785 ,775 ,757 ,733 ,713 ,697 ,686 ,676 ,668 ,666 ]
_out=[400   ,500 ,1000,1500,2000,2500,3000,3500,4000,4500,5000]

def multiMap(val, _in, _out, size):
  #// take care the value is within range
  #// val = constrain(val, _in[0], _in[size-1]);
  if (val >= _in[0]):
    return _out[0]
  if (val <= _in[size-1]):
       return _out[size-1]

  #// search right interval
  pos = 1;  #// _in[0] allready tested
  while(val < _in[pos]):
      pos+= 1
  #// this will handle all exact "points" in the _in array
  if (val == _in[pos]):
    return _out[pos]
  #// interpolate in the right segment for the rest
  return int((val - _in[pos-1]) * (_out[pos] - _out[pos-1]) / (_in[pos] - _in[pos-1]) + _out[pos-1])



def convertToPressure(muscleLength):
    musclePressure = multiMap(muscleLength,_in,_out,11)
    return musclePressure


def FST_send(lengths):
    # todo - add exception handling for potential conversion and socket errors
    command = ""
    for idx, len in enumerate(lengths) :
        muscle = convertToPressure(len)
        command += "maw"+str(64+idx)+"="+str(muscle)+"\r\n"
    print command 
    FSTs.sendto(command,(FST_ip, FST_port))

    
class MyTCPHandler(SocketServer.StreamRequestHandler):
        
    def handle(self):   
        while True:     
            try:         
                json_str = self.rfile.readline().strip()[2:]
                if json_str != None:                          
                    print json_str
                    #print "{} wrote:".format(self.client_address[0])       
                    try:                 
                        j = json.loads(json_str)                
                        # print "got:", j                          
                        if j['method'] == 'moveEvent':  
                           #print "received a moveEvent query, parsing and sending to FST"
                           #optional reply on move receive
                           #conn.send("moving to moveEvent data")
                           #compulsory forward of data
                           lengths = j['rawArgs']                  
                           FST_send(lengths)
                           print "Sent to FST"            
                        elif j['method'] == 'geometry':
                           self.sendGeometry()
                    except ValueError:
                        print "nothing decoded"
            except : 
                  print "Connection from middleware broken, restart middleware"
                  break;   
                
        
    def sendGeometry(self):
       #todo add exception handling for send 
       g = '{"jsonrpc":"2.0","reply":"geometry","effectorName":"Chairserver","baseRadius":176,"platformRadius":216,"initialHeight":680,"maxTranslation":40,"maxRotation":25,"platformAngles":[147,154,266,274,26,33],"baseAngles":[140,207,226,314,334,40]}\n'
       print "sending geometry", g
       self.wfile.write(g)    
            
if __name__ == "__main__":
    # setup the UDP Socket  
    FST_ip = '127.0.0.1'
    FST_port = 10007 #TODO - change this back to correct festo port
    print "Chair server opening festo socket on ", FST_port
    FSTs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # start the server
    HOST, PORT = '', 10003

    # Create the server, binding to localhost on port effector port
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    print "Chair server ready to receive on port ",PORT   
    server.serve_forever()
    