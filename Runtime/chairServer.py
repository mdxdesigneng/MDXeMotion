# Chair Server
# Input messages are normalized values for the 6 muscles
# this is converted into percent of muscle length
#     0% = 666mm, 100% = 790mm
# a table read from a CSV file is interpolated to convert percent to pressure

import socket
import json
import SocketServer
import sys
import os.path
import csv
from setConsoleCaption import identifyConsoleApp

csvFname = "active.csv"

#default values used if CSV file not found
_pressures=[400  ,500 ,1000,1500,2000,2500,3000,3500,4000,4500,5000]
               
def percentToPressure(percent):     
  try:
    percent = max(min(99.99, percent), 0) #clamp negative or 100+ values
    step = 100.0/ (len(_pressures)-1)
    index = int(percent/ step)     
    musclePressure = scale((percent % step)*100/step, (0,100),( _pressures[index], _pressures[index+1]))                      
    return musclePressure
  except:
     e = sys.exc_info()[0]
     print "scale error:", e  

def scale( val, src, dst) :   # the Arduino 'map' function written in python  
  return (val - src[0]) * (dst[1] - dst[0]) / (src[1] - src[0])  + dst[0]
    
def readCSV(fname):
    if os.path.isfile(fname): 
        f = open(fname, 'rt')   
        heading = f.readline()   
        if heading == '"Category","Pressure"\n':        
            try:
                reader = csv.reader(f)
                rows = iter(reader)                      
                # todo - need exception handling here             
                _pressures = list(int(p[1]) for p in rows)
                print "Using pressures from file: ", fname
            finally:
                f.close()           
            print "pressures",_pressures            
        else:
           print "Did not find header in csv file: ", fname,", using default pressures"
    else:
       print fname," not found, using default pressures"

def pressureAdjust(pressure,idx):
    # This reduces the pressure by 500 on the back muscles. 2,3
    # And by 250 on the second to back muscles, 1,4
    _adjusts=[0,-250,-500,-500,-250,0]
    ajustedPressure = pressure + _adjusts[idx]
    return ajustedPressure


def convertToPressure(idx, percent):
    musclePressure = pressureAdjust(percentToPressure(percent),idx) 
    return musclePressure


def FST_send(percents):
    # todo - add better exception handling for potential conversion and socket errors
    try:
        for idx, percent in enumerate(percents) :
            muscle = convertToPressure(idx, percent) #idx needed for Adjustsing the pressures for muscles 2,3
            command = "maw"+str(64+idx)+"="+str(muscle)
            print command,
            command = command +"\r\n"
            try:
               FSTs.sendto(command,(FST_ip, FST_port))
            except:
               print "Error sending to Festo"
        print "\n"   
    except: 
        e = sys.exc_info()[0]
        print e

    
class MyTCPHandler(SocketServer.StreamRequestHandler):
        
    def handle(self):           
        while True:           
            try:         
                json_str = self.rfile.readline().strip()[2:]                
                if json_str != None:                          
                    #print json_str                  
                    #print "{} wrote:".format(self.client_address[0])       
                    try:                 
                        j = json.loads(json_str)                
                        #print "got:", j                                                  
                        if j['method'] == 'moveEvent':  
                           #print "received a moveEvent query, parsing and sending to FST"
                           #optional reply on move receive
                           #conn.send("moving to moveEvent data")
                           #compulsory forward of data                           #
                           percent = [ (n * 50) + 50 for n in j['rawArgs']]                          
                           print j['rawArgs'], percent                           
                           FST_send(percent)
                           #print "Sent to FST"            
                        elif j['method'] == 'geometry':
                           self.sendGeometry()                       
                    except ValueError:
                        print "nothing decoded"                       
            except : 
                  print "Connection from middleware broken, restart middleware"
                  break;   
                
        
    def sendGeometry(self):
       #todo add exception handling for send 
       g = '{"jsonrpc":"2.0","reply":"geometry","effectorName":"Chairserver","baseRadius":176,"platformRadius":216,"initialHeight":728,"maxTranslation":40,"maxRotation":25,"actuatorLen":[666,790],"platformAngles":[147,154,266,274,26,33],"baseAngles":[140,207,226,314,334,40]}\n'
       print "sending geometry", g
       self.wfile.write(g)    
            
if __name__ == "__main__":
    identifyConsoleApp()
    # replace defaults with pressure values from csv file
    readCSV('active.csv')
    
    # setup the UDP Socket  
    TESTING = True
    if TESTING:        
        FST_ip = 'localhost'
        FST_port = 991 
    else:  
       FST_ip = '192.168.10.10'
       FST_port = 991 

    print "Chair server opening festo socket on ", FST_port
    FSTs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # start the server
    HOST, PORT = '', 10003

    # Create the server, binding to localhost on port effector port
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    print "Chair server ready to receive on port ",PORT   
    server.serve_forever()
    