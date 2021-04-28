from main import API

a=API()
a.sess='AAAATlrvMaj5B1tRrTdG_YVdKwPRplka5d5_lV_i6PTtcED06tscRIVj0ifXN0xU3weXf_Eh-PNSzTMzNw7CBcLbjkT_kww941dFj4hdSc5cineU'
a.uin='393298264'
a.setRegion(2)
a.setDevice(2)
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