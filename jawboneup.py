#!/usr/bin/python
# Import data from jawbone's website, and feed the data into graphite
import requests
import json
import pprint as pp
class jawboneauth:
    def __init__(self, username, password, service='nudge'):
        self.authurl = "https://jawbone.com/user/signin/login"
        self.username = username
        self.password = password
        self.service = service
    def authentication(self):
        data = {'email': self.username, 'pwd': self.password, 'service': self.service}
        request = requests.get(self.authurl, params=data)
        jtoken = json.loads(request.text)
        result = jtoken['token']
        return result

class jawboneclient:
    def __init__(self, token):
        self.nudge_header = {'x-nudge-token': token}
        self.api_url_base = 'https://jawbone.com/nudge/api/users/@me/' 
    def moves(self):
        request = requests.get(self.api_url_base + "moves", headers = self.nudge_header )
        jload = json.loads(request.text)
        return jload 
    def goals(self):
        request = requests.get(self.api_url_base + "goals", headers = self.nudge_header )
        jload = json.loads(request.text)
        return jload 
    def sleeps(self):
        request = requests.get(self.api_url_base + "sleeps", headers = self.nudge_header )
        jload = json.loads(request.text)
        return jload 
    def trends(self):
        request = requests.get(self.api_url_base + "trends", headers = self.nudge_header )
        jload = json.loads(request.text)
        return jload 


jauth = jawboneauth('username', 'passwd')
test2 = jauth.authentication()
jcli = jawboneclient(test2)
jdata = jcli.sleeps()
pp.pprint(jdata)
