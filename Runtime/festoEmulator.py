import socket
print "Welcome to the FST Emulator"

UDP_IP = '' # listen on all adapters
UDP_PORT = 991


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:\n", data