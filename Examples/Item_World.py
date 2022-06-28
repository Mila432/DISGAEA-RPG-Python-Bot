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

min_innocent_rank = 5 # if item has an innocent with a higher rank keep
max_rarity = 70 # do not donate items above this rarity
min_item_rank = 40 # minimum rank of items to be added to the depository

# ensureDrops=True - keep retrying on stages 10,20,30... until an tem drops
# getOnlyWeapons=True - keep retrying until a weapon drops
# runLimit=10 - Number of items to complete. 0 for unlimited
# raid_farming_party - party to use to leech raid bosses. After each item run the bot will check for available booses and leech

items_to_run = 2
count=0
while(count < items_to_run):
    a.upgradeItems(ensureDrops=True, getOnlyWeapons=False, runLimit=1, raid_farming_party=0)
    a.etna_resort_check_deposit_status(min_innocent_rank, min_item_rank)
    a.sell_r40_equipment_with_no_innocents()
    count+=1