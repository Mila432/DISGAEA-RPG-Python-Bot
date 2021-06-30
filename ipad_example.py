from main import API

a=API()
a.setProxy('127.0.0.1:8888')
a.sess='AAAATlrvMaj5B1tR4VrD1Qhy3GV_zukDoYg5KF_i6PTtcED04lhQItRHCj0A9Gx_RoAIHBvWLPZloWZfGGGt_6zzGqa1dHIO9cqZdIhdSc5cineU'
a.uin='396184879'
a.wait(5)#this will wait 5 seconds between each action
a.setRegion(2)
a.setDevice(1)
a.dologin()

#use event codes
a.boltrend_exchange_code('73rss7mw9i')
a.boltrend_exchange_code('ckwwievtx9')
a.boltrend_exchange_code('dkskdyexfr')
a.boltrend_exchange_code('e7ef24evfc')
a.boltrend_exchange_code('gyka4jreqf')
a.boltrend_exchange_code('h3wq5ft9kw')
a.boltrend_exchange_code('k7uu7d6zkq')
a.boltrend_exchange_code('ksyyrtaufe')
a.boltrend_exchange_code('nuwjyu26xh')
a.boltrend_exchange_code('pe3q2hrden')
a.boltrend_exchange_code('rkxwj7qrwk')
a.boltrend_exchange_code('rr5nguvafi')

#do single quest
a.doQuest(1001101303)
#do multiple quests
a.completeStory(90101)
#farm dungeon
a.completeStory(50107,farmingAll=True)