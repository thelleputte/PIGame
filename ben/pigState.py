# coding: utf-8
import os.path
import select
import time
from subprocess import call

class PigState():
	def __init__(self, game):
		self.game = game
		self.name = "generic"

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

	def player_button_configure_gpio(self, gpio):
		self.set_gpio_direction(gpio, "in")
		self.set_gpio_active_low(gpio,"1")#if pulled up an active low comportment is more logic : button pressed = 1
		#self.set_gpio_trigger(gpio,"rising")# rising as the active_low state is true
		self.set_gpio_trigger(gpio, "falling")  # it seems to be electrical valued not logical value (active_low insensitive)

	def player_light_configure_gpio(self, gpio):
		self.set_gpio_direction(gpio, "out")
		self.set_gpio_active_low(gpio,"0") # 1 on the base of the NPN will allo current in Collector causing light on
		self.set_gpio_value(gpio, 0)  # rising as the active_low state is true

	def ack_button_configure_gpio(self, gpio):
		self.set_gpio_direction(gpio, "in")
		self.set_gpio_active_low(gpio,"1") #if pulled up an active low comportment is more logic : button pressed = 1
		self.set_gpio_trigger(gpio,"falling")

	def __str__(self):
		return self.name
	
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
		#blablabla configure players enzo voort
		call(["pull_config/pull_config", "0x02", "0x04100000", "0"])
	def handle_state(self):
		self.game.set_state(self.game.wait_for_answer_state)

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

class AskQuestionState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "ask_question"

class WaitForAnswerState(PigState):
	
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "wait_for_answer"

	def init_input_gpios(self):
		BASEDIR = '/sys/class/gpio/'
		gpios= dict()
		for p in self.game.players:
			gpios[p.id]={}
			if os.path.isdir(BASEDIR+'gpio'+str(p.gpio[0])):
				print("gpio{} exists".format(p.gpio[0]))
				gpios[p.id]["button"]=(BASEDIR+'gpio'+str(p.gpio[0]))
			else:
				retVal = open(BASEDIR+'export','w')
				retVal.write(str(p.gpio[0]))
				gpios[p.id]["button"]=(BASEDIR+'gpio'+str(p.gpio[0]))
				retVal.close()
				self.player_button_configure_gpio(gpios[p.id]["button"])
				
			if os.path.isdir(BASEDIR+'gpio'+str(p.gpio[1])):
				print("gpio{} exists".format(p.gpio[1]))
				gpios[p.id]["light"]=(BASEDIR+'gpio'+str(p.gpio[1]))
			else:
				retVal = open(BASEDIR+'export','w')
				retVal.write(str(p.gpio[1]))
				gpios[p.id]["light"]=(BASEDIR+'gpio'+str(p.gpio[1]))
				retVal.close()
				self.player_light_configure_gpio(gpios[p.id]["light"])
		#all gpios should be available (device tree should have configured these correctly)
		return gpios
	
	def handle_state(self):
		gpios = self.init_input_gpios()
		epoll = select.epoll()
		for p in self.game.players:
			gpios[p.id]["fd"]=(open(gpios[p.id]["button"] + "/value", 'r'))
			epoll.register(gpios[p.id]["fd"].fileno(), select.EPOLLPRI) #demons
			gpios[p.id]["fd"].read()
			#gpios[p.id]["fd"].seek(0,0)
		nack = open(self.game.ack_buttons["nack_button"]["path"] +"/value",'r')
		epoll.register(nack.fileno(), select.EPOLLPRI)
		nack.read()
		
		events = epoll.poll(-1)
		for fileno, event in events:
			print("longueur de events = {}".format(len(events)))
			if fileno == nack.fileno():
				nack.read()
				player = None
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
			player = [p for p in self.game.players if gpios[p.id]["fd"].fileno() == fileno]
			#player = self.game.players(gpios["buttons"].index(button))
			self.game.answer_from(player[0])
			#print("debug pigState line : {}, fastest player = {}".format(139, player))
		
		for p in self.game.players:
			epoll.unregister(gpios[p.id]["fd"])
			gpios[p.id]["fd"].close()
		epoll.unregister(nack.fileno())
		nack.close()
		epoll.close()
		
		if player is not None:
			#now that the player is known, we need to light his button
			light = open(str(gpios[player[0].id]["light"])+"/value",'w')
			light.write("1")
			light.close()
			self.game.set_state(self.game.handle_answer_state)

class HandleAnswerState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "handle_answer"
	def handle_state(self):
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
		for i in self.ack_buttons:
			fd.append((open(self.ack_buttons[i]["path"]+"/value",'r'),i))
			fd[-1][0].read()
			epoll.register(fd[-1][0].fileno(),select.EPOLLPRI)
			fd[-1][0].read()
			
			
		#wait for an action on one of the 2 buttons
		pressed_button = list()
		events = epoll.poll(-1)
		print("length of events in wait_ack {}".format(len(events)))
		for fileno, event in events:
			pressed_button.append(fileno)
			#first_press = time.perf_counter()
			#print("first press = {}".format(str(first_press)))
			for f in [x for x in fd if x[0].fileno() == fileno] :
				f[0].read()
				f[0].seek(0,0)
				active_file = f
				#debouncing :
				debounce_buffer = ['1\n']*5
				while '1\n' in debounce_buffer:
					f[0].seek(0,0)
					debounce_buffer.append(f[0].read())
					debounce_buffer.pop(0)
					#print(debounce_buffer)
					time.sleep(0.01)
				
		#keep only the pressed button in epoll list
		rem = [f for f in fd if f[0].fileno() != pressed_button[0]]
		for f in rem:
			epoll.unregister(f[0].fileno())
		epoll.unregister(active_file[0].fileno())
		# time.sleep(0.1)#debouncing
		# active_file.seek(0,0)
		# active_file.read()#have to read after registering/unregistering
		# events = epoll.poll(self.next_question_timeout)
		# second_press = time.perf_counter()-first_press
		# print("second press = {}".format(str(second_press)))
		epoll.close()
		# if len(events)<1:
			# the button has been pressed for more than next_qestion_timeout
			# that means next question please
			# return_value = None #as there is no winner for this question
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
		
		if active_file[1] == "ack_button":
			return_value = True
		else :
			return_value = False
		for f in fd:
			f[0].close()
		return return_value
		
	def handle_state(self):
		val = self.wait_ack()
		if self.game.fastest_player:
			f = open("/sys/class/gpio/gpio{}/value".format(self.game.fastest_player.gpio[1]),'w')
			f.write("0")
		if val is True :
			print("good answer, give the point ")
			#give the point
			print("thz score before = {}".format(self.game.fastest_player.score))
			self.game.fastest_player.score+=1
			#reset the fastest player
			self.game.answer_from(None) 
			#go to next state
			self.game.set_state(self.game.wait_for_answer_state)
		elif val is False:
			print("bad answer")
			#bad answer, go to wait for answer
			self.game.answer_from(None) 
			#go to next state
			self.game.set_state(self.game.wait_for_answer_state)
			#demons should remove the fastest player from player list for next wait for answer
		else: #should be None => next question
			print("next question please line 264")
			#reset the fastest player
			self.game.answer_from(None)
			#demons : we should reset the list of player as we go to next question
			#go to next state
			self.game.set_state(self.game.wait_for_answer_state)

class AnswerAckState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "answer_ack"

