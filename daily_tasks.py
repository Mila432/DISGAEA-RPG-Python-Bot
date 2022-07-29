import datetime
import os

from dateutil import parser

from api.constants import Constants
from main import API

a = API()
a.config(
    sess=os.getenv('DRPG_TOKEN'),
    uin=os.getenv('DRPG_UIN'),
    wait=0,
    region=2,
    device=2
)

a.quick_login()

# Send sardines
player_data = a.client.player_index()
if player_data['result']['act_give_count']['act_send_count'] == 0:
    a.client.friend_send_sardines()

# Buy items from HL shop
a.buy_daily_items_from_shop()

# Use free gacha
last_free_gacha_at_string = player_data['result']['status']['last_free_gacha_at']
last_free_gacha_at_string_date = parser.parse(last_free_gacha_at_string)
serverTime = datetime.datetime.utcnow() + datetime.timedelta(hours=-4)
server_date = serverTime.date()
last_free_gacha_date = last_free_gacha_at_string_date.date()
if server_date > last_free_gacha_date:
    print("free gacha available")
    a.get_free_gacha()

# Spin bingo
bingo_data = a.client.bingo_index(Constants.Current_Bingo_ID)
if not bingo_data['result']['t_bingo_data']['drew_today']:
    spin_result = a.client.bingo_lottery(Constants.Current_Bingo_ID, False)
    if 'api_error' in spin_result:
        print(spin_result['api_error']['message'])
    else:
        spin_index = spin_result['result']['t_bingo_data']['last_bingo_index']
        print(f"Bingo spinned. Obtained number {bingo_data['result']['t_bingo_data']['display_numbers'][spin_index]}.")
        free_reward_positions = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        bingo_rewards = bingo_data['result']['rewards']
        free_rewards = [bingo_rewards[i] for i in free_reward_positions]
        available_free_rewards = [x for x in free_rewards if x['status'] == 1]
        if len(available_free_rewards) > 0:
            print(f"There are {len(available_free_rewards)} free rewards available to claim.")

# Buy all items with innocents, refresh shop, sell items without rare innos
# shop_rank = player_data['result']['status']['shop_rank']
# a.shop_change_equipment_items(shop_rank)
# a.BuyAllEquipmentWithInnocents()
# a.innocent_safe_sellItems()

# Calculate when AP is filled
player_data = a.client.player_index()
current_ap = player_data['result']['status']['act']
max_ap = player_data['result']['status']['act_max']
ap_filled_date = datetime.datetime.now() + datetime.timedelta(minutes=(max_ap - current_ap) * 2)

# last roulete time in utc -4. Spins available every 8 hours
lastRouleteTimeString = a.client.hospital_index()['result']['last_hospital_at']
lastRouletteTime = parser.parse(lastRouleteTimeString)
utcminus4time = datetime.datetime.utcnow() + datetime.timedelta(hours=-4)
if utcminus4time > lastRouletteTime + datetime.timedelta(hours=8):
    result = a.client.hospital_roulette()
