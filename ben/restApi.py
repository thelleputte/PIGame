from http.server import BaseHTTPRequestHandler, HTTPServer
#import SocketServer
import json
#import random
from threading import Thread

class S(BaseHTTPRequestHandler):
	the_game = None
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		#we don't want to send anything
		self.send_header('Content-length', 0)
		self._set_headers()
		#f = open("index.html", "r")

		#self.wfile.write(f.read())

	def do_HEAD(self):
		self._set_headers()

	def do_POST(self):
		self._set_headers()
		print("in post method")
		self.data_string = self.rfile.read(int(self.headers['Content-Length'])).decode("utf-8")
		self.send_response(200)
		self.end_headers()

		data = json.loads(self.data_string)
		print ("{}".format(data))
		self.wfile.write('OK\n\n'.encode('utf-8'))
		##print(S.the_game)
		#todo : implement the API here to change player names or remove players from the game !!
		# The key command line to test  curl -H "Content-Type: application/json" -X POST -d '{"username":"xyz","password":"xyz"}' http://localhost:10005
		if data["command"]=="set_name":
			player_id = data["args"]["id"]
			new_name = data["args"]["name"]
			players = S.the_game.players
			player = [p for p in players if p.id == player_id][0]
			player.name = new_name
		# what are the other commands ?
		# remove player => a player will be removed from the game (have to check that in details to avoid errors during the current turn)
		if data["command"]=="remove_player":
			player_id = data["args"]["id"]
			players = S.the_game.players
			player = [p for p in players if p.id == player_id][0]
			if player not in S.the_game.players_to_remove:
				S.the_game.players_to_remove.append(player)
			#the player will be removed for next question.
		# load question file

		#before leaving this method, update the status message and send it to all listeners to get them up to date.
		S.the_game.send_message(S.the_game.registred_interfaces, S.the_game.update_status_message())
		return

class RestApi(Thread):
	def __init__(self, game):
		Thread.__init__(self)
		self.game = game  # give an access to the game for player modifications
		self.server_class = HTTPServer
		self.handler_class = S
		self.handler_class.the_game = game
		self.port = 10005
	def run(self):
		server_address = ('', self.port)
		httpd = self.server_class(server_address, self.handler_class)
		print ('Starting httpd...')
		httpd.serve_forever()

