# coding: utf-8
import os.path
import select
import time
from subprocess import call
import json
import socket
import random
from player import *
from questionLoader import *

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

class PigState():
	BASEDIR = '/sys/class/gpio/'
	def __init__(self, game):
		self.game = game
		self.name = "generic"
		self.generic_http_response = "HTTP/1.1 200 OK\nContent-Length: 0\nAccess-Control-Allow-Origin: *\nConnection: Close\n\n".encode('utf-8')
	def handle_state(self):
		#self.game.update_status_message()
		self.game.send_message(self.game.registred_interfaces,self.game.update_status_message())
		#self.game.send_message(self.game.registred_interfaces,json.dumps(self.game.status_message).encode('utf-8'))
		
	# define GPIO configuration functions
	def set_gpio_direction(self, gpio, state):
		retVal = open(gpio + "/direction", 'w')
		retVal.write(state)
		retVal.close()
	
	def set_gpio_trigger(self, gpio, edge):
		retVal = open(gpio + "/edge", 'w')
		retVal.write(edge)
		retVal.close
	
	def set_gpio_active_low(self, gpio, string_flag):
		retVal = open(gpio + "/active_low", 'w')
		retVal.write(string_flag)
		retVal.close()
	
	def set_gpio_value(self, gpio, value):
		retVal = open(gpio + "/value", 'w')
		retVal.write(str(value))
		retVal.close()
	
	def get_gpio_value(self, gpio, value):
		retVal = open(gpio + "/value", 'r')
		result = retVal.read()
		retVal.close()
		return result

	def check_gpio(self, gpio):
		path = PigState.BASEDIR + 'gpio' + str(gpio)
		if os.path.isdir(path):
			print("gpio{} exists".format(gpio))
		else:
			retVal = open(PigState.BASEDIR + 'export', 'w')
			retVal.write(str(gpio))
			retVal.close()
		return path

	def player_button_configure_gpio(self, gpio):
		path = self.check_gpio(gpio)
		self.set_gpio_direction(path, "in")
		self.set_gpio_active_low(path,"1")#if pulled up an active low comportment is more logic : button pressed = 1
		#self.set_gpio_trigger(gpio,"rising")# rising as the active_low state is true
		self.set_gpio_trigger(path, "falling")  # it seems to be electrical valued not logical value (active_low insensitive)
	
	def player_light_configure_gpio(self, gpio):
		path = self.check_gpio(gpio)
		self.set_gpio_direction(path, "out")
		self.set_gpio_active_low(path,"0") # 1 on the base of the NPN will allo current in Collector causing light on
		self.set_gpio_value(path, 0)
	
	def ack_button_configure_gpio(self, gpio):
		#self.check_gpio(gpio)#demons to modify for uniformity
		self.set_gpio_direction(gpio, "in")
		self.set_gpio_active_low(gpio,"1") #if pulled up an active low comportment is more logic : button pressed = 1
		self.set_gpio_trigger(gpio,"both")

	def get_gpio_value_path(self, gpio):
		return PigState.BASEDIR + 'gpio' + str(gpio) + '/value'

	def set_player_light(self, player, status='1'):
		fd = open(self.get_gpio_value_path(player.led), 'w')
		fd.write(status)
		fd.close()

	def __str__(self):
		return self.name

class InterfaceInitState(PigState):
	def __init__(self, game):
		self.game = game
		self.name = "Interface_init"
	def handle_state(self):
		super(InterfaceInitState, self).handle_state()
		self.game.set_communication_socket()
		self.game.set_state(self.game.init_state)


class InitState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "init"
		#configure pull-ups for player buttons
		#call(["pull_config/pull_config", "0x02", "0x02855000", "0"])
		#configure no-pull for lights
		#call(["pull_config/pull_config", "0x00", "0x00420A50", "0"])
		#do the same for ack_b uttons
		self.game.ack_buttons = self.configure_ack_buttons()
		#self.game.socket_ports={'ack':10001, 'nack':10002,'next':10003,'end':10004}#defined in piGame
		#call(["pull_config/pull_config", "0x02", "0x04100000", "0"])
		#configure all possible players GPIO as they have to be active for the registration procedure
		for b in self.game.GPIO_player_buttons :
			#print("init gpio" + str(b))
			self.player_button_configure_gpio(b)
		for l in self.game.GPIO_player_leds:
			self.player_light_configure_gpio(l)
			#print("init gpio" + str(l))
		
	def handle_state(self):
		super(InitState, self).handle_state()
		#demons we should perhaps manage game.question_dir
		if self.game.question_file:
			self.game.questions = QuestionLoader(game.question_file)
		else:
			self.game.questions = QuestionLoader()

		self.game.communication_socket.start()
		#self.game.set_state(self.game.wait_for_answer_state)
		self.game.set_state(self.game.init_players_state)
	
	def configure_ack_buttons(self, io_numbers=[20, 26]):
		BASEDIR = '/sys/class/gpio/'
		io={"ack_button":{"io_nb":io_numbers[0]},"nack_button":{"io_nb":io_numbers[1]}}
		for i in io :
			if os.path.isdir(BASEDIR + 'gpio' + str(io[i]["io_nb"])):
				print("gpio{} exists".format(io[i]["io_nb"]))
				io[i]["path"] = (BASEDIR + 'gpio' + str(io[i]["io_nb"]))
			else:
				retVal = open(BASEDIR + 'export', 'w')
				retVal.write(str(io[i]["io_nb"]))
				io[i]["path"] = (BASEDIR + 'gpio' + str(io[i]["io_nb"]))
				retVal.close()
			#ios are exported now they have to be configured
			self.ack_button_configure_gpio(io[i]["path"])
			#self.set_gpio_active_low(io[i]["path"],"1")
			#self.set_gpio_direction(io[i]["path"],"in")
			#self.set_gpio_trigger(io[i]["path"],"both")
		return io

class InitPlayersState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "init_players"
	def handle_state(self):
		super(InitPlayersState, self).handle_state()
		#here we have to implement the player registration procedure
		#first ligth on and off all players buttons to show your are waiting for player init
		dummy_players = list()
		for i in range(len(self.game.GPIO_player_leds)):
			dummy_players.append(Player(i, self.game.GPIO_player_buttons[i], self.game.GPIO_player_leds[i], "Player_{}".format(i)))

		if not self.game.simu:
			finished = False
		else:
			finished = True #players have to be hard configured in simulation mode
		while True:
			#0.5s blink
			for p in dummy_players:
				self.set_player_light(p, '1')
			time.sleep(0.5)
			for p in dummy_players:
				self.set_player_light(p, '0')

			input_gpios = dict()
			epoll = select.epoll()
			for p in dummy_players:
				fd = open(self.get_gpio_value_path(p.button), 'r')
				input_gpios[fd.fileno()] = {'fd': fd, 'player': p}
				epoll.register(fd.fileno(), select.EPOLLPRI)  # demons
				fd.read()
			ack = open(self.game.ack_buttons["ack_button"]["path"] + "/value", 'r')
			epoll.register(ack.fileno(), select.EPOLLPRI)
			ack.read()
			ack_socket = PigSocket(self.game.socket_ports['ack'])
			# ack_socket.listen()
			epoll.register(ack_socket.fileno, select.EPOLLIN)

			player = None
			events = epoll.poll(-1)
			for fileno, event in events:
				print("longueur de events = {}".format(len(events)))
				if fileno == ack.fileno():
					#the game may begin
					ack.read()
					# debouncing :
					debounce_buffer = ['1\n'] * 5
					while '1\n' in debounce_buffer:
						ack.seek(0, 0)
						debounce_buffer.append(nack.read())
						debounce_buffer.pop(0)
						time.sleep(0.01)
					finished = True
					break
				if fileno == ack_socket.fileno:
					s = ack_socket.accept()
					# I don't mind what is the information as I now it from the used port
					# works with python to python but not with browser that retries
					# so we can reply whith a generic http 200 code
					s.send(self.generic_http_response)
					# still buggy with direct browser call due to favicon.ico subrequest.  What about javascript ajax style request ?
					s.close()
					finished = True
					break
				#as no ack/ack_socket has been detected it should be a player
				player = input_gpios[fileno]['player']
				break
			#close everything
			for f in input_gpios:
				epoll.unregister(input_gpios[f]["fd"])
				input_gpios[f]["fd"].close()
			epoll.unregister(ack.fileno())
			epoll.unregister(ack_socket.fileno)
			ack.close()
			ack_socket.close()
			# add ther player to the game
			if player :
				self.game.add_player(player)
				dummy_players.remove(player)
				print('player {} has been added to the game'.format(player.name))
				self.game.send_message(self.game.registred_interfaces, self.game.update_status_message())
				self.set_player_light(player, '1')
			if finished or not len(dummy_players):
				break #if there are no more dummy players or if ack has been pressed exit the while loop
		if len(self.game.players):
			# then go to the first question
			self.game.set_state(self.game.ask_question_state)
		else: #no players in the game re-init please
			self.game.set_state(self.game.init_state)

class AskQuestionState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "ask_question"

	def handle_state(self):
		super(AskQuestionState, self).handle_state()
		for p in self.game.players_to_remove:
			self.game.remove_player(p)
		#all the players to be removed have been removed => reset the list
		self.game.players_to_remove =list();
		#reset the valid player list.
		self.game.valid_players = list(self.game.players) #copy of the player list
		try:
			(q,a) = self.game.questions.get_question_answer(remove=1)
		except EmptyQuestionListException:
			print("hehehe no more questions !! we should go to end of the game state... and notify the interface")
			(q,a)=("in n'y a plus de question", "ni de réponse\n d'ailleurs")
			#demons !!!! end of the game no more questions
		#question should be updated when an answer is ack or nacked
		self.game.send_message(self.game.registred_interfaces, self.game.update_question_message(question=q, answer=a))
		# self.game.send_message(self.game.registred_interfaces, json.dumps(self.game.question_message).encode('utf-8'))
		self.game.set_state(self.game.wait_for_answer_state)

class WaitForAnswerState(PigState):	
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "wait_for_answer"
	
	# def init_input_gpios(self):
	# 	BASEDIR = '/sys/class/gpio/'
	# 	gpios= dict()
	# 	for p in self.game.players:
	# 		gpios[p.id]={}
	# 		if os.path.isdir(BASEDIR+'gpio'+str(p.gpio[0])):
	# 			print("gpio{} exists".format(p.gpio[0]))
	# 			gpios[p.id]["button"]=(BASEDIR+'gpio'+str(p.gpio[0]))
	# 		else:
	# 			retVal = open(BASEDIR+'export','w')
	# 			retVal.write(str(p.gpio[0]))
	# 			gpios[p.id]["button"]=(BASEDIR+'gpio'+str(p.gpio[0]))
	# 			retVal.close()
	# 			self.player_button_configure_gpio(gpios[p.id]["button"])
	#
	# 		if os.path.isdir(BASEDIR+'gpio'+str(p.gpio[1])):
	# 			print("gpio{} exists".format(p.gpio[1]))
	# 			gpios[p.id]["light"]=(BASEDIR+'gpio'+str(p.gpio[1]))
	# 		else:
	# 			retVal = open(BASEDIR+'export','w')
	# 			retVal.write(str(p.gpio[1]))
	# 			gpios[p.id]["light"]=(BASEDIR+'gpio'+str(p.gpio[1]))
	# 			retVal.close()
	# 			self.player_light_configure_gpio(gpios[p.id]["light"])
	# 	#all gpios should be available (device tree should have configured these correctly)
	# 	return gpios


	def handle_state(self):
		super(WaitForAnswerState, self).handle_state()
		input_gpios=dict()
		#debug print
		print("----- DEBUG Valid Users -----\n {}\n------------------".format([n.name for n in self.game.valid_players]))
		if not self.game.simu:
			# gpios = self.init_input_gpios()
			epoll = select.epoll()
			for p in self.game.valid_players:
				#gpios[p.id]["fd"]=(open(gpios[p.id]["button"] + "/value", 'r'))
				fd = open(self.get_gpio_value_path(p.button) , 'r')
				input_gpios[fd.fileno()]={'fd':fd,'player':p }
				epoll.register(fd.fileno(), select.EPOLLPRI) #demons
				fd.read()
			nack = open(self.game.ack_buttons["nack_button"]["path"] +"/value",'r')
			epoll.register(nack.fileno(), select.EPOLLPRI)
			nack.read()
			nack_socket = PigSocket(self.game.socket_ports['nack'])
			#nack_socket.listen()
			end_socket = PigSocket(self.game.socket_ports['end'])
			#end_socket.listen()
			next_socket = PigSocket(self.game.socket_ports['next'])
			#next_socket.listen()
			epoll.register(nack_socket.fileno, select.EPOLLIN)
			epoll.register(end_socket.fileno, select.EPOLLIN)
			epoll.register(next_socket.fileno, select.EPOLLIN)

			events = epoll.poll(-1)
			for fileno, event in events:
				print("longueur de events = {}".format(len(events)))
				player = None
				if fileno == nack.fileno():
					nack.read()
					self.game.answer_from(player)
					print("Next Question Please !!")
					self.game.set_state(self.game.wait_for_answer_state)
					#debouncing :
					debounce_buffer = ['1\n']*5
					while '1\n' in debounce_buffer:
						nack.seek(0,0)
						debounce_buffer.append(nack.read())
						debounce_buffer.pop(0)
						time.sleep(0.01)
					break
				if fileno == nack_socket.fileno or fileno == next_socket.fileno:
					s=nack_socket.accept() if fileno == nack_socket.fileno else next_socket.accept()
					#I don't mind what is the information as I now it from the used port
					#works with python to python but not with browser that retry
					s.send(self.generic_http_response)
					s.close()
					self.game.answer_from(player)
					print("Next Question Please !!")
					self.game.set_state(self.game.ask_question_state)
					break
				if fileno == end_socket.fileno:
					s=end_socket.accept()
					#I don't mind what is the information as I now it from the used port
					#works with python to python but not with browser that retries
					#so we can reply whith a generic http 200 code
					s.send(self.generic_http_response)
					# still buggy with direct browser call due to favicon.ico subrequest.  What about javascript ajax style request ?
					s.close()
					self.game.answer_from(player)
					print("End of the game !!, this state is still not implemented")
					self.game.set_state(self.game.wait_for_answer_state)#just to avoid to be frozen in "no state" demons !!!
					break
				player = input_gpios[fileno]['player']
				#player = self.game.players(gpios["buttons"].index(button))
				self.game.answer_from(player)
				#print("debug pigState line : {}, fastest player = {}".format(139, player))

			for f in input_gpios:
				epoll.unregister(input_gpios[f]["fd"])
				input_gpios[f]["fd"].close()
			epoll.unregister(nack.fileno())
			nack.close()
			nack_socket.close()
			next_socket.close()
			end_socket.close()
			epoll.close()

			if player is not None:
				#now that the player is known, we need to light his button
				self.set_player_light(player,status='1')
				#now that the HW is OK, we can update the web interface
				self.game.send_message(self.game.registred_interfaces, self.game.update_fastest_player_message(player))
				self.game.set_state(self.game.handle_answer_state)
		else:
			#simulation mode
			print("Simulation Mode")
			#self.init_input_gpios() #have to be done even if we are in simulation mode
			r=random.randrange(len(self.game.valid_players))
			print("random index choosen : {}".format(r))
			time.sleep(5)
			player=self.game.valid_players[r]
			print("the choosen player is {}".format(player.name))
			self.game.answer_from(player)
			self.game.send_message(self.game.registred_interfaces, self.game.update_fastest_player_message(player))
			self.game.set_state(self.game.handle_answer_state)

class HandleAnswerState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "handle_answer"
	def handle_state(self):
		super(HandleAnswerState, self).handle_state()
		self.game.set_state(self.game.wait_for_answer_ack_state)
		#faut il un cas handle answer ??? si oui pour y faire quoi ?
		#éventuellement pour allumer la lampe mais c'est déjà fait dans wait_for_answer
		#peut etre à revoir.


class WaitForAnswerAckState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "wait_for_answer_ack"
		self.ack_buttons = self.game.ack_buttons
		self.next_question_timeout = 2

	def wait_ack(self):
		fd = list()
		epoll = select.epoll()
		registered_buttons = dict() 
		registered_sock = dict()
		for i in self.ack_buttons:
			fd.append((open(self.ack_buttons[i]["path"]+"/value",'r'),i))
			epoll.register(fd[-1][0].fileno(),select.EPOLLPRI)
			fd[-1][0].read()
			registered_buttons[fd[-1][0].fileno()] = {'button':i, 'file_desc' : fd[-1][0]}
		#create sockets on ack, nack and end 
		ack_socket = PigSocket(self.game.socket_ports['ack'])
		nack_socket = PigSocket(self.game.socket_ports['nack'])
		end_socket = PigSocket(self.game.socket_ports['end'])
		
		epoll.register(ack_socket.fileno, select.EPOLLIN)
		registered_sock[ack_socket.fileno] = {'button' :'ack_socket', 'file_desc':ack_socket}
		epoll.register(nack_socket.fileno, select.EPOLLIN)	
		registered_sock[nack_socket.fileno] = {'button' :'nack_socket', 'file_desc':nack_socket}
		epoll.register(end_socket.fileno, select.EPOLLIN)
		registered_sock[end_socket.fileno] = {'button' :'end_socket', 'file_desc':end_socket}
				
		#wait for an action on one button or socket
		pressed_button = list()
		events = epoll.poll(-1)
		print("length of events in wait_ack {}".format(len(events)))
		for fileno, event in events:
			#pressed_button.append(fileno)
			#first_press = time.perf_counter()
			#print("first press = {}".format(str(first_press)))
			#for f in [x for x in fd if x[0].fileno() == fileno] :
			if fileno in registered_buttons:
				#f[0].read()
				registered_buttons[fileno]['file_desc'].read()
				#f[0].seek(0,0)
				registered_buttons[fileno]['file_desc'].seek(0,0)
				active_file = registered_buttons[fileno]
				#debouncing :
				debounce_buffer = ['1\n']*5
				while '1\n' in debounce_buffer:
					#f[0].seek(0,0)
					registered_buttons[fileno]['file_desc'].seek(0,0)
					debounce_buffer.append(registered_buttons[fileno]['file_desc'].read())
					debounce_buffer.pop(0)
					#print(debounce_buffer)
					time.sleep(0.01)	
		#keep only the pressed button in epoll list
		#rem = [f for f in fd if f[0].fileno() != pressed_button[0]]
		#for f in rem:
		#	epoll.unregister(f[0].fileno())
		#epoll.unregister(active_file[0].fileno())
		#events = epoll.poll(self.next_question_timeout)
			if fileno in registered_sock:
				active_file = registered_sock[fileno]
				s= active_file['file_desc'].accept()
				s.send(self.generic_http_response)
				s.close()
							
		
		#unregister all
		# for f in registered_buttons.values():
			# f[file_desc].close()
		for f in merge_two_dicts(registered_buttons, registered_sock):		#merge of both dict
			epoll.unregister(f)
		epoll.close()
		#if len(events)<1:
			#the button has been pressed for more than next_qestion_timeout
			#that means next question please
			#return_value = None #as there is no winner for this question
		# else :
			# for fileno, event in events:
				# ack= [a[1] for a in fd if a[0].fileno() == fileno]
				# print(ack[0])
				# if ack[0] == "ack_button":
					# return_value = True
				# elif ack[0] == "nack_button":
					# return_value = False
				# else:
					# return_value = None #demons
		if active_file['button'] == "ack_button":
			return_value = True
		elif active_file['button'] == "nack_button":
			return_value = False
		elif active_file['button'] == "ack_socket":
			return_value = True
		elif active_file['button'] == "nack_socket":
			return_value = False
		elif active_file['button'] == "end_socket":
			return_value = False #demons, we should do something else
		for f in merge_two_dicts(registered_buttons, registered_sock).values():
			#print(f[0])
			#f[0].close()
			f['file_desc'].close()
		return return_value
		
	def handle_state(self):
		super(WaitForAnswerAckState, self).handle_state()
		val = self.wait_ack()
		if self.game.fastest_player:
			# f = open("/sys/class/gpio/gpio{}/value".format(self.game.fastest_player.gpio[1]),'w')
			# f.write("0")
			self.set_player_light(self.game.fastest_player,status='0')
		if val is True :
			print("good answer")
			#give the point
			self.game.fastest_player.score +=1			
			#reset the fastest player
			self.game.answer_from(None) 
			#go to next state
			if max([s.score for s in self.game.players])>= self.game.max_score:
				self.game.set_state(self.game.end_game_state)
			else:
				self.game.set_state(self.game.ask_question_state)
		elif val is False:
			print("bad answer")
			#bad answer, go to wait for answer
			self.game.valid_players.remove(self.game.fastest_player)
			self.game.answer_from(None)
			#go to next state
			if self.game.valid_players :
				self.game.set_state(self.game.wait_for_answer_state)
			else: #no more players in the list => next question please
				self.game.set_state(self.game.ask_question_state)
			#demons should remove the fastest player from player list for next wait for answer
		else: #should be None => next question
			print("next question please")
			#reset the fastest player
			self.game.answer_from(None)
			#demons : we should reset the list of player as we go to next question do we ?
			#go to next state
			self.game.set_state(self.game.ask_question_state)

class AnswerAckState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "answer_ack"
		
class EndGameState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "end_game"
	def reset(self):
		#demons !!! we should reset a lot of things and switch to another state
		print("Reset Not implemented yet...")
		pass;
	def handle_state(self):
		super(EndGameState, self).handle_state()
		fd = list()
		epoll = select.epoll()
		registered_buttons = dict() 
		registered_sock = dict()
		fd.append((open(self.game.ack_buttons["ack_button"]["path"]+"/value",'r'),0))
		fd.append((open(self.game.ack_buttons["nack_button"]["path"]+"/value",'r'),1))
		for i in range(len(fd)):
			epoll.register(fd[i][0].fileno(),select.EPOLLPRI)
			fd[i][0].read()
			registered_buttons[fd[i][0].fileno()] = {'button':i, 'file_desc' : fd[i][0]}
		
		#create sockets on ack 
		ack_socket = PigSocket(self.game.socket_ports['ack'])
		#no nack_socket at the end of the game if you want to shutdown press red button on the pig
		#nack_socket = PigSocket(self.game.socket_ports['nack'])
		
		epoll.register(ack_socket.fileno, select.EPOLLIN)
		registered_sock[ack_socket.fileno] = {'button' :'ack_socket', 'file_desc':ack_socket}
		#epoll.register(nack_socket.fileno, select.EPOLLIN)	
		#registered_sock[nack_socket.fileno] = {'button' :'nack_socket', 'file_desc':nack_socket}
		pressed_button = list()
		print(registered_sock)
		events = epoll.poll(-1)
		print("length of events in wait_ack {}".format(len(events)))
		for fileno, event in events:
			if fileno in registered_buttons:
				registered_buttons[fileno]['file_desc'].read()
				registered_buttons[fileno]['file_desc'].seek(0,0)
				active_file = registered_buttons[fileno]
				#debouncing :
				debounce_buffer = ['1\n']*5
				while '1\n' in debounce_buffer:
					#f[0].seek(0,0)
					registered_buttons[fileno]['file_desc'].seek(0,0)
					debounce_buffer.append(registered_buttons[fileno]['file_desc'].read())
					debounce_buffer.pop(0)
					#print(debounce_buffer)
					time.sleep(0.01)	
		#keep only the pressed button in epoll list
		#rem = [f for f in fd if f[0].fileno() != pressed_button[0]]
		#for f in rem:
		#	epoll.unregister(f[0].fileno())
		#epoll.unregister(active_file[0].fileno())
		#events = epoll.poll(self.next_question_timeout)
			if fileno in registered_sock:
				active_file = registered_sock[fileno]
				s= active_file['file_desc'].accept()
				s.send(self.generic_http_response)
				s.close()
							
		
		#unregister all
		# for f in registered_buttons.values():
			# f[file_desc].close()
		for f in merge_two_dicts(registered_buttons, registered_sock):		#merge of both dict
			epoll.unregister(f)
		epoll.close()
		if active_file['button'] == "ack_button" or active_file['button'] == "ack_socket":
			print("yesss ils en redemandent")
			self.reset();
		if active_file['button'] == "nack_button":
			print("go to sleep !!!")
			call(["poweroff"])
		


class PigSocket():
	def __init__(self, port, bind_address="0.0.0.0", nb_conn=1):
		self.serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serversocket.bind((bind_address, port))
		self.serversocket.listen(nb_conn)
		self.serversocket.setblocking(0)
	
	def close(self):
		self.serversocket.close()
	
	#def listen(self):
	#	self.serversocket.listen()
	@property
	def fileno(self):
		return self.serversocket.fileno()
	def accept(self):
		s, port=self.serversocket.accept()
		print("socket {}, port {}".format(s,port))
		return s

