#!/usr/bin/python
#bfgminer api integration to feed to graphite
# by Joshua Jackson <tsunam@gmail.com>

import socket
import sys
import json
import pprint
from optparse import OptionParser

class Bfgminer:
	def __init__(self, command="summary", host="localhost", port=4028):
		self.hostname = host
		self.port = port
		self.command = command

	def comm(self):
		data = ''
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect((self.hostname, int(self.port)))
			sock.send(json.dumps({"command": self.command}))
			while True:
				newdata = sock.recv(1024)
				if newdata:
					data += newdata
				else:
					break
		finally:
			sock.close()
		if data:
			#replace null bytes
			received = json.loads(data.replace('\x00', ''))
		return(received)


def options():
	parser = OptionParser()
	parser.add_option("-s", "--server", dest="hostname", help="hostname of bfgminer instance", metavar="HOSTNAME", default="localhost")
	parser.add_option("-p", "--port", dest="port", help="port for api access", metavar="PORT", default=4028)
	return parser

def main():
	arguments = options()
	(opts, args) = arguments.parse_args()
	sections = [ "summary", "pools", "devs" ]
	data = ''
	for request in sections:
		bapi = Bfgminer(request, opts.hostname, opts.port)
		test = bapi.comm()
		print pprint.pprint(test)

if __name__=="__main__":
	main()	
