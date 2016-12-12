import os.path
import select
import time
class PigState():
	def __init__(self, game):
		self.game = game
		self.name = "generic"

	def __str__(self):
		return self.name
	
class InitState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "init"
		#blablabla configure players enzo voort
		
	def handle_state(self):
		self.game.set_state(self.game.wait_for_answer_state)
		
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
				
			if os.path.isdir(BASEDIR+'gpio'+str(p.gpio[1])):
				print("gpio{} exists".format(p.gpio[1]))
				gpios[p.id]["light"]=(BASEDIR+'gpio'+str(p.gpio[1]))
			else:
				retVal = open(BASEDIR+'export','w')
				retVal.write(str(p.gpio[1]))
				gpios[p.id]["light"]=(BASEDIR+'gpio'+str(p.gpio[1]))
				retVal.close()
		#all gpios should be available (device tree should have configured these correctly)
		return gpios
	
	def handle_state(self):
		gpios = self.init_input_gpios()
		epoll = select.epoll()
		for p in self.game.players:
			gpios[p.id]["fd"]=(open(gpios[p.id]["button"] + "/value", 'r'))
			epoll.register(gpios[p.id]["fd"].fileno(), select.EPOLLPRI) #demons
			gpios[p.id]["fd"].read()
		events = epoll.poll(-1)
		for fileno, event in events:
			player = [p for p in self.game.players if gpios[p.id]["fd"].fileno() == fileno]
			#player = self.game.players(gpios["buttons"].index(button))
			self.game.answer_from(player)
		for p in self.game.players:
			epoll.unregister(gpios[p.id]["fd"])
			gpios[p.id]["fd"].close()
		epoll.close()
		
		#now that the player is known, we need to light his button
		light = open(gpios[player.id]["light"]+"/value",'w')
		light.write(1)
		light.close()
		self.game.set_state(self.game.handle_answer_state)

class HandleAnswerState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "handle_answer"

class WaitForAnswerAckState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "wait_for_answer_ack"

class AnswerAckState(PigState):
	def __init__(self, game):
		PigState.__init__(self, game)
		self.name = "answer_ack"

