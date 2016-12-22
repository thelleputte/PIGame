class Player():
	GPIO=[(14, 4), (18,17), (23,22), (25,9), (12,11), (16,6)];#first=button second = light
	def __init__(self, id, name = None):
		if name:
			self._name = name
		else:
			self._name = "Player {}".format(id)
		self._score = 0
		self.id = id
		self._gpio = Player.GPIO[id]
	
	@property
	def name(self) :
		return self._name
	
	@name.setter
	def name(self, name) :
		self._name = name
	
	@property
	def gpio(self) :
		return self._gpio
	
	@property
	def score(self) :
		return self._score
	
	@score.setter
	def score(self, score) :
		print("the score {}".format(score))
		self._score = score
	
	def __str__(self):
		output = "id: {id}\t name: {name}\t score: {score}".format(id=str(self.id), name=self._name, score=str(self._score))
		return output