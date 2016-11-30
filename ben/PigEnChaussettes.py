#!/usr/bin/python

import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.setblocking(False)
#sock.settimeout(10)
#in this example I let the sock socket blocking so that it waits for connection until a connection occurs
# Bind the socket to the port
server_address = ('localhost', 10000)
#print(server_address(0))
print ('starting up on {} port {}'.format(server_address[0],server_address[1]))
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
	print('waiting for a connection')
	connection, client_address = sock.accept()
	#connection is also a socket, it should be timed out
	connection.settimeout(10)
	try:
		print ('connection from', client_address)
		connection.sendall(b'hello fucking world\b')
        # Receive the data in small chunks and retransmit it
		cnt = 0
		while True:
			print(str(cnt))
			cnt+=1
			data = connection.recv(16)
			print ('received {}'.format(data))
			if data:
				print ('sending data back to the client')
				connection.sendall(data)
			else:
				print('no more data from {}'.format(client_address))
				break
	finally:
        # Clean up the connection
			connection.close()