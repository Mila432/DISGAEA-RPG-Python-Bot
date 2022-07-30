import io
import json
import os

data = {}
pwd = os.path.dirname(__file__)

for f in os.listdir(pwd):
    if '.json' not in f:
        continue
    with io.open(os.path.join(pwd, f), encoding='utf8') as fj:
        data[f.split('.')[0]] = json.load(fj)
