# -*- coding: utf-8 -*-
import requests
import base64
import json
import time
import sys
import os

class codedbots(object):
	def __init__(self):
		self.s=requests.Session()
		self.license='PUT YOUR LICENSE KEY HERE'
		if len(self.license)!=64:
			print('license invalid')
			exit(1)
		self.mainurl=base64.b64decode('aHR0cHM6Ly9kaXNnYWVhLmNvZGVkYm90cy5jb20=').decode()
		self.key=None

	def rndid(self):
		if sys.version_info >= (3, 0):
			return os.urandom(16).hex()
		return os.urandom(16).encode('hex')

	def randomiv(self):
		return self.s.get(self.mainurl+'/iv').content

	def encrypt(self,data,iv):
		r= self.s.post(self.mainurl+'/encrypt',data={'data':base64.b64encode(json.dumps(data).encode()),'iv':iv,'license':self.license,'fuji_key':self.key})
		if r.status_code==200:
			return base64.b64decode(r.content)
		else:
			print('[%s] license key invalid or blocked [%s]'%(r.status_code,self.license))
			time.sleep(60)
			return None

	def decrypt(self,data,iv):
		r= self.s.post(self.mainurl+'/decrypt',data={'data':data,'iv':iv,'fuji_key':self.key,'license':self.license})
		if r.status_code==200:
			return json.loads(base64.b64decode(r.content))
		else:
			print('[%s] license key invalid or blocked [%s]'%(r.status_code,self.license))
			time.sleep(60)
			return None