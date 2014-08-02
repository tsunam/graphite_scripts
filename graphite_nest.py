#!/usr/bin/python
# graphite_nest - Nest api integration to feed data into Graphite
# by Joshua Jackson, tsunam@gmail.com
# A plugin for graphite to read from the nest api and write the resulting information 
# Based in part off Scott M Bakers nest.py http://www.smbaker.com/

import urllib2
import urllib
import sys
import pickle
import socket
import time
import struct
import yaml
import os

try:
	import json
except ImportError:
	print "No json library installed please install python-json"
	sys.exit(1)

def temperature(value):
	fahrenheit = (value * 1.8) + 32
	return fahrenheit

def miles(value):
	mph = (value * .621371)
	return mph

class Nest:
	def __init__(self, user, password, serial=None, metric=False, name=False):
		self.username = user
		self.password = password
		self.serial = serial
		self.metric = metric
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
		self.structure_id = rep["structure"].keys()[0]
		#Grab zipcode to use with weather_url api
		self.zipcode = rep["structure"][self.structure_id]["postal_code"]
		result = self.nest_devices()
		return(result)

	def nest_devices(self):
		self.device_list = []
		if (self.serial is False):
			self.device_id = self.repsave["structure"][self.structure_id]["devices"]
			#devices are a combo of device.serial
			for device in self.device_id:
				self.device_list.append(device.split(".")[1])
		else:
			self.device_list.append(self.serial)
		result = self.nest_serial()
		return(result)

	def nest_serial(self):
		weather = self.nest_weather()
		for device in self.device_list:
			self.device = {}
			#pull all potentially interesting values
			self.device["battery_level"] = self.repsave["device"][device]["battery_level"]
			self.device["interior_humidity"] =self.repsave["device"][device]["current_humidity"]
			self.device["learning_days_completed_cool"] = self.repsave["device"][device]["learning_days_completed_cool"]
			self.device["learning_days_completed_heat"] = self.repsave["device"][device]["learning_days_completed_heat"]
			self.device["learning_days_completed_range"] = self.repsave["device"][device]["learning_days_completed_range"]
			self.device["learning_time"] = self.repsave["device"][device]["learning_time"]
			self.device["time_to_target_temp"] = self.repsave["device"][device]["time_to_target"]
			if (self.metric is True):
				self.device["current_temperature"] = self.repsave["shared"][device]["current_temperature"]
			else:
				self.device["current_temperature"] = temperature(self.repsave["shared"][device]["current_temperature"])
			if (self.name is True):
				self.device["name"] = self.repsave["shared"][device]["name"]
			else:
				self.device["name"] = device 
			self.device.update(weather)
		return(self.device)

	def nest_weather(self):
		self.weather = {}
		req = urllib2.Request(self.weather_url + self.zipcode)
		res = urllib2.urlopen(req).read()
		rep = json.loads(res)
		self.weather["temperature"] = rep[self.zipcode]["current"]["temp_c"]
		if (self.metric is True):
			self.weather["windspeed"] = rep[self.zipcode]["current"]["wind_kph"]
		else:
			self.weather["windspeed"] = miles(rep[self.zipcode]["current"]["wind_kph"])
		self.weather["exterior_humidity"] = rep[self.zipcode]["current"]["humidity"]
		self.weather["lengthofday"] = rep[self.zipcode]["current"]["lengthofday"]
		return(self.weather)

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
			pickled.append(( self.prefix + "." + self.data["name"] + "." + key, ( epoch, value)))
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

def main():
	config = yaml.load(open(os.path.expanduser("~") + "/.config/" + "graphite/" + "settings.cfg","r").read())
	napi = Nest(config["user"], config["password"], config["serial"], config["metric"], config["name"])
	napi.nest_auth()
	data = napi.nest_structure()
	graphite = Graphite(data, config["graphite_prefix"], config["graphite_host"],config["graphite_port"])
	graphite.pickling()

if __name__=="__main__":
	main()	
