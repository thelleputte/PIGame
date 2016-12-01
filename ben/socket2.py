#!/usr/bin/python

#inspired from https://pymotw.com/2/select/
import select
import socket
import sys
import queue
import time

try :
	# Create a TCP/IP socket
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)
	maxMessages = 100
	# Bind the socket to the port
	server_address = ('localhost', 10000)
	print('starting up on {} port {}\n'.format(server_address[0], server_address[1]))
	server.bind(server_address)

	# Listen for incoming connections
	server.listen(5)
	# Sockets from which we expect to read
	inputs = [server]

	# Sockets to which we expect to write
	outputs = [ ]
	# Outgoing message queues (socket:Queue)
	message_queues = {}
	ind = 0
	while inputs:
		# Wait for at least one of the sockets to be ready for processing
		#print('waiting for the next event\n')
		readable, writable, exceptional = select.select(inputs, outputs, inputs,2)
		 # Handle inputs
		for s in readable:
			if s is server:
				# A "readable" server socket is ready to accept a connection
				connection, client_address = s.accept()
				print ('new connection from' + client_address[0] + str(client_address[1]))
				connection.setblocking(0)
				inputs.append(connection)
				# Give the connection a queue for data we want to send
				message_queues[connection] = queue.Queue()
			else:
				data = s.recv(16)
				if data:
					# A readable client socket has data
					print ('received {} '.format(data))
					message_queues[s].put(data)
					# Add output channel for response
					if s not in outputs:
						outputs.append(s)
				else:
					# Interpret empty result as closed connection
					print( 'closing ' + str(client_address)+ ' after reading no data')
					# Stop listening for input on the connection
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()
					# Remove message queue
					del message_queues[s]
		# Handle outputs
		for s in writable:
			try:
				next_msg = message_queues[s].get_nowait()
				if ind < maxMessages:
					message_queues[s].put(str(time.time()).encode('utf-8'))
					ind +=1

			except queue.Empty:
				# No messages waiting so stop checking for writability.
				print('output queue for '+ str(s.getpeername()) + ' is empty')
				outputs.remove(s)
			else:
				#try:
				print('sending {} to {}'.format(next_msg, s.getpeername()))
				s.send(next_msg)
				#except :
					# print ('outch socket already dead')
					# if s in inputs :
					# 	inputs.remove(s)
					# if s in outputs :
					# 	outputs.remove(s)
					# 	del message_queues[s]
		# Handle "exceptional conditions"
		for s in exceptional:
			print('handling exceptional condition for ' + str(s.getpeername()))
			# Stop listening for input on the connection
			inputs.remove(s)
			if s in outputs:
				outputs.remove(s)
			s.close()

			# Remove message queue
			del message_queues[s]
except KeyboardInterrupt :
	for s in inputs:
		try:
			print('closing connection for ' +str(s.getpeername()))
			s.close()
		except OSError:
			print('socket already destroyed')
	for s in outputs:
		try:
			print('closing connection for ' +str(s.getpeername()))
			s.close
		except OSError:
			print('socket already destroyed')
