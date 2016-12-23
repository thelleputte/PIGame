from pigState import *
from player import *
from socketListener import *
import select

class PiGame():
	def __init__(self):
		#players infos
		self._nb_players = 6
		self.players = list();#to be updated
		self.fastest_player = None

		#states
		self.interface_init_state = InterfaceInitState(self)
		self.init_state = InitState(self)
		self.wait_for_answer_state = WaitForAnswerState(self)
		self.handle_answer_state = HandleAnswerState(self)
		self.wait_for_answer_ack_state = WaitForAnswerAckState(self)
		self.state = self.interface_init_state

		#sockets
		self.registred_interfaces = list()

		#status message
		self.status_message={"type" : "status","state":"", "nb_players": self._nb_players,
						"player names": [p.name for p in self.players], "scores": [p.score for p in self.players]}

	def set_communicatio_socket(self):
		self.communication_socket = SocketListener(ip="0.0.0.0", port=10000, game=self, nb_conn=10) #demons est ce ok de passer self depuis la méthode init ?

	def register_socket(self, open_socket):
		self.registred_interfaces.append(open_socket)
		if open_socket[1][1] == 10000 :
			print("communication socket register")
			self.communication_epoll.register(open_socket[0].fileno(),select.EPOLLIN)

	def send_message(self,sockets, message):
		epoll = select.epoll()
		connections={}
		bytes_written = {}
		try:
			for c,ad in sockets:
				epoll.register(c.fileno(),select.EPOLLOUT)
				connections[c.fileno()] = c
				bytes_written[c.fileno()] = 0

			events = epoll.poll(1)
			for fileno, event in events:
				bytes_written[fileno] = connections[fileno].send(message)
				if event & select.EPOLLHUP:
					epoll.unregister(fileno)
					connections[fileno].close()
					sockets.remove(s for s in sockets if sockets[0] == connections[fileno])
					del connections[fileno]
		finally:
			epoll.close()

	def answer_from(self, player):
		try:
			print("player {pl} was the fastest".format(pl=player.name))
		except AttributeError:
			print("no name to display, no player got the right answer")
		self.fastest_player = player
	
	def set_state(self, state):
		self.state = state
		self.status_message["state"] = state.name
	
	@property
	def nb_players(self):
		return self._nb_players

	@nb_players.setter
	def nb_players(self,nb):
		self._nb_players = nb

	def add_player(self, player):
		self.players.append(player)

	def __str__(self):
		#print("we aer here")
		output=""
		for p in self.players :
			output += str(p) +"\n"
		output += str(self.state)
		return output

if __name__ == '__main__':
	the_game = PiGame()
	the_game.nb_players = 1
	p1 = Player(0, name="ben")
	the_game.add_player(p1)
	for i in range(12):
		the_game.state.handle_state();
		print(the_game)
 