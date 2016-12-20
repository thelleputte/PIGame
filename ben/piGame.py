from pigState import *
from player import *
class PiGame():
	def __init__(self):
		self._nb_players = 6
		self.players = list();#to be updated
		
		self.init_state = InitState(self)
		self.wait_for_answer_state =WaitForAnswerState(self)
		self.handle_answer_state =HandleAnswerState(self)
		self.state = self.init_state

	def answer_from(self, player):
		print("player {pl} was the fastest".format(pl=player.name))
	
	def set_state(self, state):
		self.state = state
	
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
	for i in range(2):
		the_game.state.handle_state();
		print(the_game)
 