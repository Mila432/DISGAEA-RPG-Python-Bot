import json
import os
import io

data = {}
pwd=os.path.dirname(__file__)

for f in os.listdir(pwd):
	if '.json' not in f:	continue
	region=2 if '_gl' in f else 1
	with io.open(os.path.join(pwd,f), encoding='utf8') as fj:
		data[region][f.split('.')[0]]=json.load(fj)