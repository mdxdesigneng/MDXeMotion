import socket
import json

# Set up a TCP/IP socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# Connect as client to a selected server
# on a specified port
s.connect(("127.0.0.1",2020))

# Protocol exchange - sends and receives




samplejson = '{"jsonrpc":"2.0","method":"moveEvent","rawArgs":[750, 750, 740, 760, 740, 750], "xyzrpyArgs":[0.0, 0.0, 0.1, -0.2, 0.0, 0.0], "extents":[40,25,700,800]}'
s.send(samplejson)

# Close the connection when completed
s.close()
print "\ndone"

