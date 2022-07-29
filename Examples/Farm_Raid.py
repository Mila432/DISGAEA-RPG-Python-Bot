import datetime
import time

from dateutil import parser

from api.constants import Constants
from main import API

a = API()
a.config(
    sess=Constants.session_id,
    uin=Constants.user_id,
    wait=0,
    region=2,
    device=2
)
a.dologin()

# Farm Raid endlessly
# use hospital roulete when available
# When AP is filled, runs Axel contest until stage 50 for one character

party_to_use = 9
boss_count = 0

# last roulete time seems to be in utc -4. Spins available every 8 hours
lastRouleteTimeString = a.client.hospital_index()['result']['last_hospital_at']
lastRouletteTime = parser.parse(lastRouleteTimeString)

player_data = a.client.player_index()
current_ap = player_data['result']['status']['act']
max_ap = player_data['result']['status']['act_max']
ap_filled_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=(max_ap - current_ap) * 2)

while True:

    serverTime = datetime.datetime.utcnow() + datetime.timedelta(hours=-4)
    if serverTime > lastRouletteTime + datetime.timedelta(hours=8):
        result = a.client.hospital_roulette()
        lastRouleteTimeString = a.client.hospital_index()['result']['last_hospital_at']
        lastRouletteTime = parser.parse(lastRouleteTimeString)

    if datetime.datetime.utcnow() > ap_filled_date or current_ap >= max_ap:
        a.do_axel_contest_multiple_characters(1, 50)
        player_data = a.client.player_index()
        current_ap = player_data['result']['status']['act']
        max_ap = player_data['result']['status']['act_max']
        ap_filled_date = datetime.datetime.now() + datetime.timedelta(minutes=(max_ap - current_ap) * 2)

    available_raid_bosses = a.raid_find_all_available_bosses()
    for raid_boss in available_raid_bosses:
        raid_stage_id = a.raid_find_stageid(raid_boss['m_raid_boss_id'], raid_boss['level'])
        if raid_stage_id != 0:
            battle_start_data = a.raid_battle_start(raid_stage_id, raid_boss['id'], party_to_use)
            battle_end_data = a.raid_battle_end_giveup(raid_stage_id, raid_boss['id'])
            boss_count += 1
            print(f"Farmed boss with level {raid_boss['level']}. Total bosses farmed: {boss_count}")
    time.sleep(10)
