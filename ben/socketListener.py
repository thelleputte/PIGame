from socket import *
import select

class SocketListener():
    def __init__(self, ip="0.0.0.0", port=10000, game=None, nb_conn=10):
        self.server = (ip, port)
        #self.nb_conn = nb_conn

        #setup the socket
        self.serversocket = socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.serversocket.bind((ip, port))
        self.serversocket.listen(nb_conn)
        self.serversocket.setblocking(0)

        #setup the epoll
        self.epoll = select.epoll()
        #register the socket as input socket.
        self.epoll.register(self.serversocket.fileno(), select.EPOLLIN)

    #add custom functions here


    def destroy(self):
        self.epoll.unregister(self.serversocket.fileno())
        self.epoll.close()
        self.serversocket.close()