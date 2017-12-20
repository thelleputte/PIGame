from pigState import *
from player import *
from socketListener import *
from restApi import *
import select
import json
import sys

class PiGame():
	#static definitions of USED PLAYERS GPIOS
	GPIO_player_buttons = 	[14, 18, 23, 25,  8, 12]
	GPIO_player_leds = 		[ 4, 17, 22,  9, 11,  6]
	#these values on a RPI1 please
	#GPIO_player_buttons = 	[14, 18, 23, 25,  8]
	#GPIO_player_leds = 		[ 4, 17, 22,  9, 11]
	def __init__(self):
		#simulation flag
		self.simu = False
		self.question_file = None
		self.question_dir = None
		self.questions = None
		self.max_score = 10

		#players infos
		self._nb_players = 0
		self.players = list();#to be updated
		self.valid_players = list();# list of players that may answer
		self.fastest_player = None
		self.players_to_remove = list()# list of player that will be removed from the game at next question

		#states
		self.interface_init_state = InterfaceInitState(self)
		self.init_state = InitState(self)
		self.init_players_state = InitPlayersState(self)
		self.ask_question_state = AskQuestionState(self)
		self.wait_for_answer_state = WaitForAnswerState(self)
		self.handle_answer_state = HandleAnswerState(self)
		self.wait_for_answer_ack_state = WaitForAnswerAckState(self)
		self.end_game_state = EndGameState(self)
		self.state = self.interface_init_state

		#sockets
		self.registred_interfaces = list()
		self.socket_ports={'ack':10001, 'nack':10002,'next':10003,'end':10004}

		#status message
		self.status_message={"type" : "status","state":"",
							 "nb_players": self._nb_players,
							 "player ids" : [p.id for p in self.players],
							 "player names": [p.name for p in self.players],
							 "scores": [p.score for p in self.players]}
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
		self.status_message["player ids"] = [p.id for p in self.players]
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

	def set_communication_socket(self):
		print("set the communication socket")
		self.communication_socket = SocketListener(ip="0.0.0.0", port=10000, game=self, nb_conn=10) 
		self.communication_epoll = select.epoll()
		self.apiSocket = RestApi(self)
		self.apiSocket.start()
		
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

			#send status on new connection (to all peers ?)
			if self.state is self.ask_question_state or self.state is self.wait_for_answer_state \
				or self.state is self.handle_answer_state or self.state is self.wait_for_answer_ack_state:
				#we should re-send the question
				print("resend the question to the new interface")
				question_message = self.event_header + \
								   "id: <any_id>\n" \
								   "event: question\n" \
								   "data: {}\n\n".format(json.dumps(self.question_message)).encode('utf-8')
				self.send_message([open_socket], question_message)
			self.send_message([open_socket], self.update_status_message())
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
		self.valid_players.append(player)
		self.nb_players +=1

	def remove_player(self, player):
		self.players.remove(player)
		#if the remove is done before copying the player list in valid_players we don't have to remove from valid_players
		#self.valid_players.append(player)
		self.nb_players -= 1

	def __str__(self):
		#print("we aer here")
		output=""
		for p in self.players :
			output += str(p) +"\n"
		output += "\033[31;1m"+str(self.state)+"\033[0m"
		return output

if __name__ == '__main__':
	the_game = PiGame()
	if len(sys.argv) > 1:
		the_game.simu = int(sys.argv[1])
		print("Simulation mode {}".format(the_game.simu))
	if len(sys.argv)>2:
		the_game.question_file = str(sys.argv[2])
	#the_game.nb_players = 1
	if the_game.simu:
		pl=list()
		pl.append(Player(0,PiGame.GPIO_player_buttons[0], PiGame.GPIO_player_leds[0], name="Clara"))
		pl.append(Player(1, PiGame.GPIO_player_buttons[1], PiGame.GPIO_player_leds[1], name="Inès"))
		pl.append(Player(2, PiGame.GPIO_player_buttons[2], PiGame.GPIO_player_leds[2], name="Dorian"))
		pl.append(Player(3, PiGame.GPIO_player_buttons[3], PiGame.GPIO_player_leds[3], name="Coline"))
		pl.append(Player(4, PiGame.GPIO_player_buttons[4], PiGame.GPIO_player_leds[4], name="Quentin"))
		#pl.append( Player(5,name='Remi')) #do not use the 6th player with a RPI 1 : GPIO6 writing crashes the system
		for p in pl:
			the_game.add_player(p)

	#for i in range(12):
	while 1:
		the_game.state.handle_state();
		print(the_game)
 