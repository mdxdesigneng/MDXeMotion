# Let's setup the TCP server
import socket
import json


port = 2020
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print socket.gethostname() 
s.bind(('', port))
s.listen(1)

# Let's setup the UDP Socket  
FST_ip = '127.0.0.1'
FST_port = 5005
FSTs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Instead of listening for connections, we'll connect to the server.

print "Chair server is running on port", port
print "Chair server is running on hostname", socket.gethostname()




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



def FST_send(moveEventJson):
	parsed_json = json.loads(data)
	rawArgs = parsed_json['rawArgs']
	command = ""
	for idx,muscle in enumerate(rawArgs):
		muscle = convertToPressure(muscle)
		command += "maw"+str(64+idx)+"="+str(muscle)+"\r\n"
	print command 
	FSTs.sendto(command,(FST_ip, FST_port))



while 1: 
	conn, addr = s.accept() 
	try:
		data = conn.recv(1024)
		data = data.decode('utf-8')

		# display client connection information
		data = data.strip()
		print "ChairServer recieved:", data


		parsed_json = json.loads(data)
		if parsed_json['method'] == "moveEvent":
			print "revieved a moveEvent query, parsing and sending to FST"
			#optional reply on move recieve
			#conn.send("moving to moveEvent data")
			#compulsary forward of data
			FST_send(data)
			print "Sent to FST"
		
		if parsed_json['method'] == "geometry":
			print "revieved a geometry query"
			#send geom data
			conn.send('{"jsonrpc":"2.0", "reply":"geometry", "effectorName":Platform Sim", "baseRadius":400, baseAngles":[140, 207, 226, 314, 334, 40]}')
			print "replied with a geometry message"


	except KeyboardInterrupt:
		#close TCP/UDP sessions
		conn.close()
		FSTs.close()




