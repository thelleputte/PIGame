import socket
import select
from threading import Thread

class SocketListener(Thread):
	def __init__(self, ip="0.0.0.0", port=10000, game=None, nb_conn=10):
		Thread.__init__(self)
		self.server = (ip, port)
		#self.nb_conn = nb_conn
		self.game = game
		#setup the socket
		self.serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serversocket.bind((ip, port))
		self.serversocket.listen(nb_conn)
		self.serversocket.setblocking(0)

		#setup the epoll
		self.epoll = select.epoll()
		#register the socket as input socket.
		self.epoll.register(self.serversocket.fileno(), select.EPOLLIN)

	def run(self):
		print("Thread started")
		while True:
			events = self.epoll.poll(1)
			for fileno, event in events:
				print("the seversocket {} the triggered fileno {}".format(self.serversocket.fileno(),fileno))
				if fileno == self.serversocket.fileno():
					print("an event on the serverSocket")
					connection, address = self.serversocket.accept()
					connection.setblocking(0)
					#add this socket to the listers of the game
					self.game.register_socket((connection, address))

	def destroy(self):
		self.epoll.unregister(self.serversocket.fileno())
		self.epoll.close()
		self.serversocket.close()

if __name__ == '__main__':
	srvSock = SocketListener()
