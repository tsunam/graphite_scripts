#!/usr/bin/python
# graphite_nest - Nest api integration to feed data into Graphite
# by Joshua Jackson, tsunam@gmail.com
# A plugin for graphite to read from the nest api and write the resulting information 
# Based in part off Scott M Bakers nest.py http://www.smbaker.com/

import urllib2
import urllib
import sys
#import pprint
from optparse import OptionParser

try:
	import json
except ImportError:
	print "No json library installed please install python-json"
	sys.exit(1)

class Nest:
	def __init__(self, user, password, serial=None, metric=False, device=None, name=False):
		self.username = user
		self.password = password
		self.serial = serial
		self.metric = metric
		self.device = device
		self.name = name
	
	def nest_auth(self):
		auth_string = urllib.urlencode({"username": self.username, "password": self.password})
		req = urllib2.Request("https://home.nest.com/user/login", auth_string, {"user-agent":"graphite_nest v/1.0"})
		res = urllib2.urlopen(req).read()
		#take json returned string and actually parse it into json
		res = json.loads(res)
		#load variables required for additional requests
		#transport is where future requests should go to
		self.transport_url = res["urls"]["transport_url"]
		#access token is for authentication of requests after the initial login
		self.access_token = res["access_token"]
		#user id is a unique id per customer, is used as part of the access token as well
		self.userid = res["userid"]
		#weather api
		self.weather_url = res["urls"]["weather_url"]
	def nest_structure(self):
		req = urllib2.Request(self.transport_url + "/v2/mobile/user." + self.userid, headers={"user-agent":"graphite_nest v/1.0", "Authorization":"Basic " + self.access_token,  "X-nl-user-id": self.userid, "X-nl-protocol-version": "1"})
		res = urllib2.urlopen(req).read()
		rep = json.loads(res)
		#save reply to work from for all future requests in other functions
		self.repsave = rep
		#pprint.pprint(rep)
		self.structure_id = rep["structure"].keys()[0]
		#Grab zipcode to use with weather_url api
		self.zipcode = rep["structure"][self.structure_id]["postal_code"]
		self.nest_devices()

	def nest_devices(self):
		if (self.device is None):
			self.device_id = self.repsave["structure"][self.structure_id]["devices"]
			self.device_list = []
			#devices are a combo of device.serial
			for device in self.device_id:
				self.device_list.append(device.split(".")[1])
		else:
			self.device_list = self.device
		self.nest_serial()

	def nest_serial(self):
		for device in self.device_list:
			self.device = []
			#pull all potentially interesting values
			self.device.append(self.repsave["device"][device]["battery_level"])
			self.device.append(self.repsave["device"][device]["current_humidity"])
			self.device.append(self.repsave["device"][device]["learning_days_completed_cool"])
			self.device.append(self.repsave["device"][device]["learning_days_completed_heat"])
			self.device.append(self.repsave["device"][device]["learning_days_completed_range"])
			self.device.append(self.repsave["device"][device]["learning_time"])
			self.device.append(self.repsave["device"][device]["time_to_target"])
			self.device.append(self.repsave["shared"][device]["current_temperature"])
			if (self.name is True):
				self.device.append(self.repsave["shared"][device]["name"])
		print self.device

def options():
	parser = OptionParser()
	parser.add_option("-u", "--user", dest="user", help="username for home.nest.com", metavar="USER", default=None)
	parser.add_option("-p", "--password", dest="password", help="password for home.nest.com", metavar="PASSWORD", default=None)
	parser.add_option("-s", "--serial", dest="serial", default=None, help="Optional: specific nest device to talk to")
	parser.add_option("-m", "--metric", dest="metric", action="store_true", help="Optional: switch to metric measurements")
	parser.add_option("-d", "--device", dest="device", default=None, help="Optional: particular device to poll")
	parser.add_option("-c", "--commonname", dest="name", action="store_true", help="Optional: Use name set for device instead of serial")
	return parser


def main():
	arguments = options()
	(opts, args) = arguments.parse_args()
	if (not opts.user) or (not opts.password):
		print "Username and Password required for home.nest.com api integration"
		sys.exit(1)
	napi = Nest(opts.user, opts.password, opts.serial, opts.metric, opts.device, opts.name)
	napi.nest_auth()
	napi.nest_structure()

if __name__=="__main__":
	main()	
