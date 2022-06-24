import datetime
import random
from dateutil import parser
import time
from api.constants import Constants
from main import API

a = API()
a.sess = ''
a.uin = ''
a.wait(0)
a.setRegion(2)
a.setDevice(2)
a.dologin()

#configure
item_world_party = 4
raid_farming_party = 9
a.setActiveParty(item_world_party)
a.minrarity(10)

# ensureDrops=True - keep retrying on stages 10,20,30... until an tem drops
# getOnlyWeapons=True - keep retrying until a weapon drops
# runLimit=10 - Number of items to complete. 0 for unlimited
# raid_farming_party - party to use to leech raid bosses. After each item run the bot will check for available booses and leech
a.upgradeItems(ensureDrops=True, getOnlyWeapons=False, runLimit=10, raid_farming_party=9)