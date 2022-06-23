from abc import ABCMeta
import random
from api.constants import Constants
from data import data as gamedata

class Raid(metaclass=ABCMeta):
    
    def __init__(self):
        super().__init__()

    def raid_battle_start(self, stage_id, raid_status_id, raid_party):
        data = self.rpc('battle/start', 
            {
                "m_stage_id":stage_id,
                "help_t_player_id":0,
                "help_t_character_id":0,
                "help_t_character_lv":0,
                "t_deck_no":raid_party,
                "m_guest_character_id":0,
                "t_character_ids":[],
                "t_memory_ids":[],
                "t_raid_status_id":raid_status_id,
                "act":0,
                "auto_rebirth_t_character_ids":[]
                })
        return data

    def raid_battle_end_giveup(self, stage_id, raid_status_id):
        data = self.rpc('battle/end', 
            {
                "m_stage_id":stage_id,
                "m_tower_no":0,
                "equipment_id":0,
                "equipment_type":0,
                "innocent_dead_flg":0,
                "t_raid_status_id":raid_status_id,
                "raid_battle_result":"eyJhbGciOiJIUzI1NiJ9.eyJoamptZmN3Njc4NXVwanpjIjowLCJzOW5lM2ttYWFuNWZxZHZ3Ijo5MDAsImQ0Y2RrbncyOGYyZjVubmwiOjUsInJnajVvbTVxOWNubDYxemIiOltdfQ.U7hhaGeDBZ3lYvgkh0ScrlJbamtNgSXvvaqsqUcZYOU",
                "m_character_id":0,
                "division_battle_result":"",
                "battle_type":1,
                "result":0,
                "battle_exp_data":[],
                "common_battle_result":"eyJhbGciOiJIUzI1NiJ9.eyJoZmJtNzg0a2hrMjYzOXBmIjoiIiwieXBiMjgydXR0eno3NjJ3eCI6MCwiZHBwY2JldzltejhjdXd3biI6MCwiemFjc3Y2amV2NGl3emp6bSI6MCwia3lxeW5pM25ubTNpMmFxYSI6MCwiZWNobTZ0aHR6Y2o0eXR5dCI6MCwiZWt1c3ZhcGdwcGlrMzVqaiI6MCwieGE1ZTMyMm1nZWo0ZjR5cSI6MH0.9DYl6QK2TkTIq81M98itbAqafdUE4nIPTYB_pp_NTd4",
                "skip_party_update_flg":True
            })
        return data

    def get_battle_exp_data_raid(self, start, deck):
        characters_in_deck = [x for x in deck if x != 0]
        id = random.randint(0, len(characters_in_deck)-1)
        rnd_char = characters_in_deck[id]
        res = [{                                  
                    "m_enemy_id": start['result']['enemy_list'][0]['pos1'],
                    "finish_type": 1,
                    "finish_member_ids": rnd_char
                }]
        return res

    def raid_find_stageid(self, m_raid_boss_id, level):
        #1351 is regular boss, 1352 badass boss
        is_badass = m_raid_boss_id % 2 == 0
        dic = gamedata['stages']
        normal_stages = [x for x in dic if x['name'] == Constants.Current_Raid_Regular_Boss_Stage]
        badass_stages = [x for x in dic if x['name'] == Constants.Current_Raid_Badass_Boss_Stage]
        stages = []
        if is_badass:
            stages = badass_stages 
        else:    
            stages = normal_stages 

        index = -1
        if is_badass:
            if level <= 9925:
                index = 0
            if level > 9925 and level <= 10394:
                index = 2
            if level > 10394 and level <= 11080 :
                index = 3
            if level > 11080  and level <= 13138:
                index = 4
            if level > 13138 and level <= 13825:
                index = 5
            if level > 13825 and level <= 15197:
                index = 6
            if level == 15883:
                index = 7
            if level > 15883 and level <= 17256 :
                index = 8
            if level == 17256:
                index = 9
            if level > 17256:
                index = 10
        if not is_badass:
            if level <= 9925:
                index = 0
            if level > 9925 and level <= 10932:
                index = 2
            if level > 10932 and level <= 12141:
                index = 3
            if level > 12141 and level <= 13149:
                index = 4
            if level > 13149 and level <= 13955:
                index = 5
            if level > 13955 and level <= 15164:
                index = 6
            if level > 15164 and level <= 16172:
                index = 7
            if level > 16172 and level <= 16978:
                index = 8
            if level > 16978 and level <= 18187:
                index = 9
            if level > 18187:
                index = 10
        if(index != -1):
            return stages[index]['id']
        return 0

    def raid_ranking_reward(self):
        data = self.rpc('raid/ranking_reward', {})
        return data

    def raid_send_help_request(self, t_raid_status_id):
        data = self.rpc('raid/help', {"t_raid_status_id": t_raid_status_id})
        return data

    def raid_give_up_boss(self, t_raid_status_id):
        data = self.rpc('raid/give_up', {"t_raid_status_id": t_raid_status_id})
        return data

    def raid_current(self):
        data = self.rpc('raid/current', {})
        return data

    def raid_history(self, raidID=Constants.Current_Raid_ID):
        data = self.rpc('raid/history', {"m_event_id":raidID})
        return data

    # reward for a specific boss battle
    def raid_reward(self, t_raid_status_id):
        data = self.rpc('raid/reward', {"t_raid_status_id": t_raid_status_id})
        return data

    def raid_gacha(self, m_event_gacha_id, lottery_num):
        data = self.rpc('event/gacha_do', {"m_event_gacha_id":m_event_gacha_id,"lottery_num":lottery_num})
        return data

    def raid_get_all_bosses(self):
        data = self.rpc('raid/index', {})
        return data['result']['t_raid_statuses']

    def raid_set_boss_level(self, m_raid_boss_id, step):
        data = self.rpc('raid_boss/update', {"m_raid_boss_id":m_raid_boss_id,"step":step})
        return data['result']

    def raid_find_all_available_bosses(self):
        all_bosses = self.raid_get_all_bosses()
        available_bosses = [x for x in all_bosses if not x['is_discoverer'] and x['current_battle_count'] < 1]
        return available_bosses

    # Will check for if there is an active boss, fight, give up and share.
    def raid_share_own_boss(self, party_to_use):
        own_boss = self.raid_current()['result']['current_t_raid_status']
        if own_boss is not None:
            #Battle and give up automatically
            if own_boss['current_battle_count'] == 0:
                raid_stage_id = self.raid_find_stageid(own_boss['m_raid_boss_id'], own_boss['level'])            
                if raid_stage_id != 0:
                    battle_start_data = self.raid_battle_start(raid_stage_id, own_boss['id'], party_to_use)
                    battle_end_data = self.raid_battle_end_giveup(raid_stage_id, own_boss['id'])
            #share
            if not own_boss['is_send_help']:
                sharing_result = self.raid_send_help_request(own_boss['id'])
                self.log("Shared boss with %s users" % sharing_result['result']['send_help_count'])

    def raid_claim_all_point_rewards(self):
        print("Claiming raid point rewards.")
        initial_stones = self.player_stone_sum()['result']['_items'][0]['num']
        raid_data = self.event_index_eventid(Constants.Current_Raid_ID)
        current_uses = raid_data['result']['events'][0]['gacha_data']['sum']
        if(current_uses == 5000):
            print(f"All rewards claimed.")
            return
        current_points = raid_data['result']['events'][0]['point']
        if(current_points < 100):
            print(f"Not enough points left to claims rewards: {current_points}")
            return
        initial_stones_spin = initial_stones
        uses_left = 5000 - current_uses
        while uses_left > 0 and current_points >=100:
            uses_to_claim = min (uses_left, 100) 
            points_needed = uses_to_claim * 100
            if(current_points < points_needed):
                uses_to_claim = current_points // 100
            data = self.raid_gacha(Constants.Current_Raid_Event_Point_Gacha, uses_to_claim)
            current_points = data['result']['after_t_data']['t_events'][0]['point']
            uses_left = 5000 - data['result']['after_t_data']['t_events'][0]['gacha_data']['sum']
            if(len(data['result']['after_t_data']['stones']) > 0):
                current_stones = data['result']['after_t_data']['stones'][0]['num']
                print(f"Nether Quartz gained: {current_stones - initial_stones_spin}")
                initial_stones_spin = current_stones
        print(f"Finished claiming raid rewards. Total Nether Quartz gained: {current_stones - initial_stones}")

    def raid_spin_innocent_roulette(self):
        print("Spinning raid innocent roulette.")
        raid_data = self.event_index_eventid(Constants.Current_Raid_ID)
        spins_left  = raid_data['result']['events'][0]['gacha_data']['chance_stock_num']
        innocent_types = gamedata['innocent_types']
        is_big_chance = raid_data['result']['events'][0]['gacha_data']['exist_big_chance']

        if(spins_left == 0 and is_big_chance is False):
            print(f"All spins used.")
            return
            
        special_spin = ""
        while spins_left > 0 or is_big_chance is True:
            data = ''
            if (is_big_chance):
                data = self.raid_gacha(Constants.Current_Raid_Innocent_Regular_Roulette, 1)
                special_spin = "Special Spin - "
            else:
                data = self.raid_gacha(Constants.Current_Raid_Innocent_Regular_Roulette, 1)
                special_spin = ""

            if('error' in data and "Invalid Parameter" in data['error']):
                print(f"Error spinning - Innocent slots are probably filled")
                return

            spins_left = data['result']['after_t_data']['t_events'][0]['gacha_data']['chance_stock_num']
            is_big_chance = data['result']['after_t_data']['t_events'][0]['gacha_data']['exist_big_chance']
            innocent_type = [x for x in innocent_types if x['ID'] == data['result']['after_t_data']['innocents'][0]['m_innocent_id']]
            print(f"{special_spin}Obtained innocent of type {innocent_type} and value: {data['result']['after_t_data']['innocents'][0]['effect_values'][0]}")                      
            
        print(f"Finished spinning the raid roulette")
    
    def raid_claim_all_boss_rewards(self):
        print("Claiming raid boss battle rewards.")
        innocent_types = gamedata['innocent_types']
        battle_logs = self.raid_history(Constants.Current_Raid_ID)['result']['battle_logs']        
        for i in battle_logs:
            if not i['already_get_present']:
                reward_data = self.raid_reward(i['t_raid_status']['id'])
                if len(reward_data['result']['after_t_data']['innocents']) > 0:
                    innocent_type = [x for x in innocent_types if x['ID'] == reward_data['result']['after_t_data']['innocents'][0]['m_innocent_id']]
                    print(f"Obtained innocent of type {innocent_type} and value: {reward_data['result']['after_t_data']['innocents'][0]['effect_values'][0]}")
        print("Finished claiming raid rewards.")
    
    def raid_farm_shared_bosses(self, party_to_use):
        boss_count = 0
        available_raid_bosses = self.raid_find_all_available_bosses()
        for raid_boss in available_raid_bosses:        
            raid_stage_id = self.raid_find_stageid(raid_boss['m_raid_boss_id'], raid_boss['level'])
            if raid_stage_id != 0:
                battle_start_data = self.raid_battle_start(raid_stage_id, raid_boss['id'], party_to_use)
                battle_end_data = self.raid_battle_end_giveup(raid_stage_id, raid_boss['id'])
                boss_count +=1
                print(f"Farmed boss with level {raid_boss['level']}. Total bosses farmed: {boss_count}")