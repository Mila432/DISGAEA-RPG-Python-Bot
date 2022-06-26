import datetime
import random
from dateutil import parser
import time
from api.constants import Constants
from main import API

a = API()
a.sess = Constants.session_id
a.uin = Constants.user_id
a.wait(0)
a.setRegion(2)
a.setDevice(2)
a.dologin()

# Send sardines
player_data = a.player_index()
if player_data['result']['act_give_count']['act_send_count'] == 0:
    a.friend_send_sardines()

#Buy items from HL shop
a.BuyDailyItemsFromShop()

# Use free gacha
last_free_gacha_at_string = player_data['result']['status']['last_free_gacha_at']
last_free_gacha_at_string_date = parser.parse(last_free_gacha_at_string)
serverTime = datetime.datetime.utcnow() + datetime.timedelta(hours=-4)
server_date = serverTime.date()
last_free_gacha_date = last_free_gacha_at_string_date.date()
if(server_date > last_free_gacha_date):
    print("free gacha available")
    a.getfreegacha()

# Spin bingo
bingo_data = a.bingo_index(Constants.Current_Bingo_ID)
if a.bingo_is_spin_available():
    spin_result = a.bingo_lottery(Constants.Current_Bingo_ID, False)
    spin_index = spin_result['result']['t_bingo_data']['last_bingo_index']
    print(f"Bingo spinned. Obtained number {spin_result['result']['t_bingo_data']['display_numbers'][spin_index]}.")
    free_reward_positions = [0,3,6,9,12,15,18,21,24,27,30,33]
    bingo_rewards =  spin_result['result']['rewards']
    free_rewards = [ bingo_rewards[i] for i in free_reward_positions ]
    available_free_rewards = [x for x in free_rewards if x['status'] == 1]  
    if(len(available_free_rewards) > 0):
        print(f"There are {len(available_free_rewards)} free rewards available to claim.")

# Shop methods, still needs improvements 
# shop_rank = player_data['result']['status']['shop_rank']
# a.shop_change_equipment_items(32)
# a.BuyAllEquipmentWithInnocents()
# a.innocent_safe_sellItems()

# Calculate when AP is filled
player_data = a.player_index()
current_ap = player_data['result']['status']['act']
max_ap = player_data['result']['status']['act_max']
ap_filled_date = datetime.datetime.now() + datetime.timedelta(minutes=(max_ap-current_ap)*2)

# Server time is utc -4. Spins available every 8 hours
lastRouleteTimeString = a.hospital_index()['result']['last_hospital_at']
lastRouletteTime = parser.parse(lastRouleteTimeString)
utcminus4time = datetime.datetime.utcnow() + datetime.timedelta(hours=-4)
if(utcminus4time > lastRouletteTime + datetime.timedelta(hours=8)):
    result = a.hospital_roulette()