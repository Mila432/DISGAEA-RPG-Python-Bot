from main import API

a = API()
a.sess = 'AAAATlrvMaj5B1tRrTdG_YVdKwPRplka5d5_lV_i6PTtcED06tscRIVj0ifXN0xU3weXf_Eh-PNSzTMzNw7CBcLbjkT_kww941dFj4hdSc5cineU'
a.uin = '393298264'
a.options.wait = 5  # this will wait 5 seconds between each action
a.options.set_region(2)
a.options.set_device(2)
a.dologin()

# use event codes
a.client.boltrend_exchange_code('73rss7mw9i')
a.client.boltrend_exchange_code('ckwwievtx9')
a.client.boltrend_exchange_code('dkskdyexfr')
a.client.boltrend_exchange_code('e7ef24evfc')
a.client.boltrend_exchange_code('gyka4jreqf')
a.client.boltrend_exchange_code('h3wq5ft9kw')
a.client.boltrend_exchange_code('k7uu7d6zkq')
a.client.boltrend_exchange_code('ksyyrtaufe')
a.client.boltrend_exchange_code('nuwjyu26xh')
a.client.boltrend_exchange_code('pe3q2hrden')
a.client.boltrend_exchange_code('rkxwj7qrwk')
a.client.boltrend_exchange_code('rr5nguvafi')

# do single quest
a.doQuest(1001101303)
# do multiple quests
a.completeStory(90101)
# farm dungeon
a.completeStory(50107, farmingAll=True)

# retry stages until min X rarity
a.options.min_rarity = 40
# farm item world
a.upgrade_items()
