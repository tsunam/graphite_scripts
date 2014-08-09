#!/usr/bin/python
#bfgminer api integration to feed to graphite
# by Joshua Jackson <tsunam@gmail.com>

import socket
import sys
import json
import pprint
import time
import pickle
import struct
from optparse import OptionParser

class Bfgminer:
	def __init__(self, command="summary", host="localhost", port=4028):
		self.hostname = socket.gethostbyname(host)
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
	def parse_devs(self, dictionary):
		device = dict()
                for item in dictionary['DEVS']:
                        device[item['Name'] + str(item['ID'])] = dict()
                        device[item['Name'] + str(item['ID'])]['Accepted'] = item['Accepted']
                        device[item['Name'] + str(item['ID'])]['Device_Hardware'] = item['Device Hardware%']
                        device[item['Name'] + str(item['ID'])]['Device_Rejected'] = item['Device Rejected%']
                        device[item['Name'] + str(item['ID'])]['Diff1_Work'] = item['Diff1 Work']
                        device[item['Name'] + str(item['ID'])]['Difficulty_Accepted'] = item['Difficulty Accepted']
                        device[item['Name'] + str(item['ID'])]['Difficulty_Rejected'] = item['Difficulty Rejected']
                        device[item['Name'] + str(item['ID'])]['Difficulty_Stale'] = item['Difficulty Stale']
                        device[item['Name'] + str(item['ID'])]['Hardware_Errors'] = item['Hardware Errors']
                        device[item['Name'] + str(item['ID'])]['ID'] = item['ID']
                        device[item['Name'] + str(item['ID'])]['Last_Share_Difficulty'] = item['Last Share Difficulty']
                        device[item['Name'] + str(item['ID'])]['MHS_20s'] = item['MHS 20s']
                        device[item['Name'] + str(item['ID'])]['MHS_av'] = item['MHS av']
                        device[item['Name'] + str(item['ID'])]['MHS_rolling'] = item['MHS rolling']
                        device[item['Name'] + str(item['ID'])]['Name'] = item['Name']
                        device[item['Name'] + str(item['ID'])]['Rejected'] = item['Rejected']
                        device[item['Name'] + str(item['ID'])]['Stale'] = item['Stale']
		return(device)
	def parse_pools(self, dictionary):
		pools = dict()
		for item in dictionary['POOLS']:
			pools['POOL' + str(item['POOL'])] = dict()
			pools['POOL' + str(item['POOL'])]['Accepted'] = item['Accepted']
			pools['POOL' + str(item['POOL'])]['Best_Share'] = item['Best Share']
			pools['POOL' + str(item['POOL'])]['Diff1_Shares'] = item['Diff1 Shares']
			pools['POOL' + str(item['POOL'])]['Difficulty_Accepted'] = item['Difficulty Accepted']
			pools['POOL' + str(item['POOL'])]['Difficulty_Rejected'] = item['Difficulty Rejected']
			pools['POOL' + str(item['POOL'])]['Difficulty_Stale'] = item['Difficulty Stale']
			pools['POOL' + str(item['POOL'])]['Discarded'] = item['Discarded']
			pools['POOL' + str(item['POOL'])]['Getworks'] = item['Getworks']
			pools['POOL' + str(item['POOL'])]['Get_Failures'] = item['Get Failures']
			pools['POOL' + str(item['POOL'])]['POOL'] = str(item['POOL'])
			pools['POOL' + str(item['POOL'])]['Pool_Rejected%'] = item['Pool Rejected%']
			pools['POOL' + str(item['POOL'])]['Pool_Stale%'] = item['Pool Stale%']
			pools['POOL' + str(item['POOL'])]['Rejected'] = item['Rejected']
			pools['POOL' + str(item['POOL'])]['Stale'] = item['Stale']
			pools['POOL' + str(item['POOL'])]['Works'] = item['Works']
		return(pools)
	def parse_coin(self, dictionary):
		coin = dict()
		for item in dictionary['COIN']:
			coin['Network_Difficulty'] = item['Network Difficulty']
		return(coin)
			
			

class Graphite:
        def __init__(self, dictionary, prefix="home.", server="localhost", port=2004):
                self.prefix = prefix
                self.server = server
                self.port = int(port)
                self.data = dictionary

        def pickling(self):
                pickled = ([])
                epoch = int(time.time())
                for key,value in self.data.iteritems():
                        pickled.append(( self.prefix + key, ( epoch, value)))
                payload = pickle.dumps(pickled)
                header = struct.pack("!L", len(payload))
                message = header + payload
                self.send_data(message)

        def send_data(self, message):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.server, self.port))
                try:
                        s.sendall(message)
                except socket.error, (value,message):
                        print "could not send message:", message
                        sys.exit(1)
                s.close()


def options():
	parser = OptionParser()
	parser.add_option("-s", "--server", dest="hostname", help="hostname of bfgminer instance", metavar="HOSTNAME", default="localhost")
	parser.add_option("-p", "--port", dest="port", help="port for api access", metavar="PORT", default=4028)
	parser.add_option("-g", "--graphite", dest="graphite", help="graphite_host", metavar="GRAPHITE", default="localhost")
	parser.add_option("-k", "--pickle", dest="pickle", help="graphite pickle port", metavar="PICKLE", default=2004)
	return parser

def main():
	arguments = options()
	(opts, args) = arguments.parse_args()
	sections = [ "pools", "devs", "coin"]
	data = ''
	diction = dict()
	for request in sections:
		diction[request.upper()] = dict() 
		bapi = Bfgminer(request, opts.hostname, opts.port)
		rep = bapi.comm()
		if "coin" in request:
			graphite = Graphite(bapi.parse_coin(rep), "home.bfgminer." + opts.hostname + "." + opts.port + ".", opts.graphite, opts.pickle)
			graphite.pickling()
		if "pools" in request:	
			pool = bapi.parse_pools(rep)
			for key in pool:
				graphite = Graphite((pool[key]), "home.bfgminer." + opts.hostname + "." + opts.port + "." + key + "." , opts.graphite, opts.pickle)
				graphite.pickling()
		if "devs" in request:
			devs = bapi.parse_devs(rep)
			for key in devs:
				graphite = Graphite((devs[key]), "home.bfgminer." + opts.hostname + "." + opts.port + "." + key + "." , opts.graphite, opts.pickle)
				graphite.pickling()
if __name__=="__main__":
	main()	
