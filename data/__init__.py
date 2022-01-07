import json
import os

data = {}
pwd=os.path.dirname(__file__)

for f in os.listdir(pwd):
	if '.json' not in f:	continue
	with open(os.path.join(pwd,f)) as fj:
		data[f.split('.')[0]]=json.load(fj)
