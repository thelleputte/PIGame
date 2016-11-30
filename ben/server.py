#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import urlparse
import subprocess
import os

class S(BaseHTTPRequestHandler):
	def _set_headers(self,type='text/html'):
		self.send_response(200)
		self.send_header('Content-type', type)
		self.end_headers()

	def do_GET(self):
		cwd = os.getcwd()
		self._set_headers()
		parsed_path = urlparse.urlparse(self.path)
		request_id = parsed_path.path
		print('parsed path: {}'.format(parsed_path))
		#response = subprocess.check_output(["python", request_id])
		#self.wfile.write(json.dumps(response))
		print('{pwd}{path}'.format(pwd=cwd, path=request_id))
		with open('{pwd}{path}'.format(pwd=cwd, path=request_id)) as f:
			self.wfile.write(f.read())
			f.close()
		#self.wfile.write('{pwd}{path}'.format(pwd=cwd, path=request_id))

	def do_POST(self):
		self._set_headers()
		parsed_path = urlparse.urlparse(self.path)
		request_id = parsed_path.path
		response = subprocess.check_output(["python", request_id])
		self.wfile.write(json.dumps(response))
		

	def do_HEAD(self):
		self._set_headers()

def run(server_class=HTTPServer, handler_class=S, port=8000):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	try:
		httpd.serve_forever()
	except:
		pass
	httpd.server_close()

if __name__ == "__main__":
	from sys import argv

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		 run()


