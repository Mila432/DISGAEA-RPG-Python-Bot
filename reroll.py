# -*- coding: utf-8 -*-
import main
import time
import proxy
import random
from multiprocessing import Pool

def login():
	a=main.API()
	#a.isReroll=True
	a.setRegion(2)
	a.setProxy(random.choice(proxy.data))
	a.reroll()
	a.getmail()
	a.updateAccount()

def preparework(s=''):
	while(1):
		try:
			login()
		except:
			pass#time.sleep(60)

def dowork():
	l=[0] * 100
	p= Pool(15)
	try:
		list(p.imap_unordered(preparework, l))
	except Exception:
		print("a worker failed, aborting...")
		p.close()
		p.terminate()
	else:
		p.close()
		p.join()
	print("job done")

if __name__ == "__main__":
	#dowork()
	preparework()
	#login()