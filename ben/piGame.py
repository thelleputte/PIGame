from pigState import *
from player import *
from socketListener import *
import select
import json
import sys

class PiGame():
	def __init__(self):
		#simulation flag
		self.simu = False

		#players infos
		self._nb_players = 6
		self.players = list();#to be updated
		self.fastest_player = None

		#states
		self.interface_init_state = InterfaceInitState(self)
		self.init_state = InitState(self)
		self.ask_question_state = AskQuestionState(self)
		self.wait_for_answer_state = WaitForAnswerState(self)
		self.handle_answer_state = HandleAnswerState(self)
		self.wait_for_answer_ack_state = WaitForAnswerAckState(self)
		self.state = self.interface_init_state

		#sockets
		self.registred_interfaces = list()

		#status message
		self.status_message={"type" : "status","state":"", "nb_players": self._nb_players,
						"player names": [p.name for p in self.players], "scores": [p.score for p in self.players]}
		#question message
		self.question_message = {"type" : "question", "question" : "The Question", "answer" : "The Answer"}

		# fastest player message
		self.fastest_player_message = {"type": "fastest_player", "player_name": "The Name", "player_id": 0}

		#event header
		self.event_header = "HTTP/1.1 200 OK\n" \
					  		"Content-Type: text/event-stream;charset=UTF-8\n"\
					  		"Access-Control-Allow-Origin: *\n\n" .encode('utf-8')

	def update_status_message(self):
		self.status_message["nb_players"] = self._nb_players
		self.status_message["player names"] = [p.name for p in self.players]
		self.status_message["scores"] = [p.score for p in self.players]
		self.status_message["state"] = self.state.name
		the_message = self.event_header +\
					  "id: <any_id>\n"\
					  "event: status\n"\
					  "data: {}\n\n".format(json.dumps(self.status_message)).encode('utf-8')
		return the_message


	def update_question_message(self, question="The Question", answer="The Answer"):
		#demons : how will it be really implemented ?
		self.question_message["question"] = question
		self.question_message["answer"] = answer
		the_message = self.event_header + \
					  "id: <any_id>\n" \
					  "event: question\n" \
					  "data: {}\n\n".format(json.dumps(self.question_message)).encode('utf-8')
		return the_message

	def update_fastest_player_message(self, player):
		self.fastest_player_message["player_name"] = player.name
		self.fastest_player_message["player_id"] = player.id
		the_message = self.event_header + \
					  "id: <any_id>\n" \
					  "event: fastest_player\n" \
					  "data: {}\n\n".format(json.dumps(self.fastest_player_message)).encode('utf-8')
		return the_message

	def set_communicatio_socket(self):
		print("set the communication socket")
		self.communication_socket = SocketListener(ip="0.0.0.0", port=10000, game=self, nb_conn=10) 
		self.communication_epoll = select.epoll()
		
	def register_socket(self, open_socket):
		self.registred_interfaces.append(open_socket)
		print("open socket{}".format(open_socket))
		print("peername {} sockname {}".format(open_socket[0].getpeername(), open_socket[0].getsockname()))
		conn, addr = open_socket
		if conn.getsockname()[1] == 10000 :
			print("communication socket register")
			# do we have to register to a poll here and pass the desired poll to send or receive message method ?
			# or doing the register when we need to send or receive a message is ok too ?
			#self.communication_epoll.register(open_socket[0].fileno(),select.EPOLLIN)

			#sse try
			# self.send_message([open_socket],"HTTP/1.1 200 OK\n"
			# 								"Content-Type: text/event-stream;charset=UTF-8\n"
			# 								"Access-Control-Allow-Origin: *\n\n"
			# 								"id: <any_id>\nevent: question\n"
			# 								"data: {}\n\n".format(json.dumps(self.question_message)).encode('utf-8'))
			self.send_message([open_socket],self.update_status_message())

			#send status on new connection (to all peers ?)
			#self.update_status_message()
			#self.send_message([open_socket],json.dumps(self.status_message).encode('utf-8'))
			#the respective decoding syntax is
			# a=json.loads(byte_message.decode('utf-8')
			
	def send_message(self,sockets, message):
		print("try to send message")
		epoll = select.epoll()
		connections={}
		bytes_written = {}
		try:
			for c,ad in sockets:
				epoll.register(c.fileno(),select.EPOLLOUT)
				connections[c.fileno()] = c
				bytes_written[c.fileno()] = 0
			#demons there should be a loop here to ensure the full message has been sent
			events = epoll.poll(1)
			for fileno, event in events:
				if event & select.EPOLLHUP:
					epoll.unregister(fileno)
					# temp = [s for s in sockets if s[0] == connections[fileno]]
					# print ("length {}".format(len(temp)))
					# print(temp)
					# print(temp[0] in sockets)
					sockets.remove([s for s in sockets if s[0] == connections[fileno]][0])
					connections[fileno].close()
					del connections[fileno]
				else:
					bytes_written[fileno] = connections[fileno].send(message)
					print("bytes_written {} for file {}".format(bytes_written[fileno], fileno))
		finally:
			epoll.close()

	def answer_from(self, player):
		try:
			print("player {pl} was the fastest".format(pl=player.name))
			#there is a player that has pressed on the button
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
	if len(sys.argv) > 1:
		the_game.simu = str(sys.argv[1])
	the_game.nb_players = 1
	p1 = Player(0, name="ben")
	the_game.add_player(p1)
	#for i in range(12):
	while 1:
		the_game.state.handle_state();
		print(the_game)
 