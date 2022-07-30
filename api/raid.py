import random
from abc import ABCMeta

from api.constants import Constants
from api.player import Player
from data import data as gamedata


class Raid(Player, metaclass=ABCMeta):

    def __init__(self):
        super().__init__()

    def raid_battle_start(self, stage_id, raid_status_id, raid_party):
        return self.client.battle_start(m_stage_id=stage_id, raid_status_id=raid_status_id,
                                        deck_no=raid_party, deck=self.pd.deck(raid_party))

    def raid_battle_end_giveup(self, stage_id, raid_status_id):
        return self.client.battle_end(
            m_stage_id=stage_id,
            battle_type=1,
            raid_status_id=raid_status_id,
            raid_battle_result="eyJhbGciOiJIUzI1NiJ9.eyJoamptZmN3Njc4NXVwanpjIjowLCJzOW5lM2ttYWFuNWZxZHZ3Ijo5MD" \
                               "AsImQ0Y2RrbncyOGYyZjVubmwiOjUsInJnajVvbTVxOWNubDYxemIiOltdfQ.U7hhaGeDBZ3lYvgkh0" \
                               "ScrlJbamtNgSXvvaqsqUcZYOU",
            common_battle_result="eyJhbGciOiJIUzI1NiJ9.eyJoZmJtNzg0a2hrMjYzOXBmIjoiIiwieXBiMjgydXR0eno3NjJ3eCI6" \
                                 "MCwiZHBwY2JldzltejhjdXd3biI6MCwiemFjc3Y2amV2NGl3emp6bSI6MCwia3lxeW5pM25ubTNpM" \
                                 "mFxYSI6MCwiZWNobTZ0aHR6Y2o0eXR5dCI6MCwiZWt1c3ZhcGdwcGlrMzVqaiI6MCwieGE1ZTMyMm" \
                                 "1nZWo0ZjR5cSI6MH0.9DYl6QK2TkTIq81M98itbAqafdUE4nIPTYB_pp_NTd4",
        )

    def get_battle_exp_data_raid(self, start, deck):
        characters_in_deck = [x for x in deck if x != 0]
        _id = random.randint(0, len(characters_in_deck) - 1)
        rnd_char = characters_in_deck[_id]
        res = [{
            "m_enemy_id": start['result']['enemy_list'][0]['pos1'],
            "finish_type": 1,
            "finish_member_ids": rnd_char
        }]
        return res

    def raid_find_stageid(self, m_raid_boss_id, level):
        # 1351 is regular boss, 1352 badass boss
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
            if level > 10394 and level <= 11080:
                index = 3
            if level > 11080 and level <= 13138:
                index = 4
            if level > 13138 and level <= 13825:
                index = 5
            if level > 13825 and level <= 15197:
                index = 6
            if level == 15883:
                index = 7
            if level > 15883 and level <= 17256:
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
        if index != -1:
            return stages[index]['id']
        return 0

    def raid_get_all_bosses(self):
        return self.client.raid_index()['result']['t_raid_statuses']

    def raid_set_boss_level(self, m_raid_boss_id, step):
        data = self.client.raid_update(m_raid_boss_id=m_raid_boss_id, step=step)
        return data['result']

    def raid_find_all_available_bosses(self):
        all_bosses = self.raid_get_all_bosses()
        available_bosses = [x for x in all_bosses if not x['is_discoverer'] and x['current_battle_count'] < 1]
        return available_bosses

    # Will check for if there is an active boss, fight, give up and share.
    def raid_share_own_boss(self, party_to_use):
        own_boss = self.client.raid_current()['result']['current_t_raid_status']
        if own_boss is not None:
            # Battle and give up automatically
            if own_boss['current_battle_count'] == 0:
                raid_stage_id = self.raid_find_stageid(own_boss['m_raid_boss_id'], own_boss['level'])
                if raid_stage_id != 0:
                    battle_start_data = self.raid_battle_start(raid_stage_id, own_boss['id'], party_to_use)
                    battle_end_data = self.raid_battle_end_giveup(raid_stage_id, own_boss['id'])
            # share
            if not own_boss['is_send_help']:
                sharing_result = self.client.raid_send_help_request(own_boss['id'])
                self.log("Shared boss with %s users" % sharing_result['result']['send_help_count'])

    def raid_claim_all_point_rewards(self):
        self.log("Claiming raid point rewards.")
        initial_stones = self.player_stone_sum()['result']['_items'][0]['num']
        raid_data = self.client.event_index(event_ids=Constants.Current_Raid_ID)
        current_uses = raid_data['result']['events'][0]['gacha_data']['sum']
        if current_uses == 5000:
            self.log(f"All rewards claimed.")
            return
        current_points = raid_data['result']['events'][0]['point']
        if current_points < 100:
            self.log(f"Not enough points left to claims rewards: {current_points}")
            return
        initial_stones_spin = initial_stones
        uses_left = 5000 - current_uses
        while uses_left > 0 and current_points >= 100:
            uses_to_claim = min(uses_left, 100)
            points_needed = uses_to_claim * 100
            if current_points < points_needed:
                uses_to_claim = current_points // 100
            data = self.client.raid_gacha(Constants.Current_Raid_Event_Point_Gacha, uses_to_claim)
            current_points = data['result']['after_t_data']['t_events'][0]['point']
            uses_left = 5000 - data['result']['after_t_data']['t_events'][0]['gacha_data']['sum']
            if len(data['result']['after_t_data']['stones']) > 0:
                current_stones = data['result']['after_t_data']['stones'][0]['num']
                self.log(f"Nether Quartz gained: {current_stones - initial_stones_spin}")
                initial_stones_spin = current_stones
        self.log(f"Finished claiming raid rewards. Total Nether Quartz gained: {current_stones - initial_stones}")

    def raid_spin_innocent_roulette(self):
        self.log("Spinning raid innocent roulette.")
        raid_data = self.client.event_index(event_ids=Constants.Current_Raid_ID)
        spins_left = raid_data['result']['events'][0]['gacha_data']['chance_stock_num']
        innocent_types = gamedata['innocent_types']
        is_big_chance = raid_data['result']['events'][0]['gacha_data']['exist_big_chance']

        if spins_left == 0 and is_big_chance is False:
            self.log(f"All spins used.")
            return

        special_spin = ""
        while spins_left > 0 or is_big_chance is True:
            data = ''
            if is_big_chance:
                data = self.client.raid_gacha(Constants.Current_Raid_Innocent_Special_Roulette, 1)
                special_spin = "Special Spin - "
            else:
                data = self.client.raid_gacha(Constants.Current_Raid_Innocent_Regular_Roulette, 1)
                special_spin = ""

            if 'error' in data and "Invalid Parameter" in data['error']:
                self.log_err(f"Error spinning - Innocent slots are probably filled")
                return

            spins_left = data['result']['after_t_data']['t_events'][0]['gacha_data']['chance_stock_num']
            is_big_chance = data['result']['after_t_data']['t_events'][0]['gacha_data']['exist_big_chance']
            innocent_type = [x for x in innocent_types if
                             x['ID'] == data['result']['after_t_data']['innocents'][0]['m_innocent_id']]
            self.log(
                f"{special_spin}Obtained innocent of type {innocent_type} and value: {data['result']['after_t_data']['innocents'][0]['effect_values'][0]}")

        self.log(f"Finished spinning the raid roulette")

    def raid_claim_all_boss_rewards(self):
        self.log("Claiming raid boss battle rewards.")
        innocent_types = gamedata['innocent_types']
        battle_logs = self.client.raid_history(Constants.Current_Raid_ID)['result']['battle_logs']
        for i in battle_logs:
            if not i['already_get_present']:
                reward_data = self.client.raid_reward(i['t_raid_status']['id'])
                if len(reward_data['result']['after_t_data']['innocents']) > 0:
                    innocent_type = [x for x in innocent_types if
                                     x['ID'] == reward_data['result']['after_t_data']['innocents'][0]['m_innocent_id']]
                    self.log(
                        f"Obtained innocent of type {innocent_type} and value: {reward_data['result']['after_t_data']['innocents'][0]['effect_values'][0]}")
        self.log("Finished claiming raid rewards.")

    def raid_farm_shared_bosses(self, party_to_use):
        boss_count = 0
        available_raid_bosses = self.raid_find_all_available_bosses()
        for raid_boss in available_raid_bosses:
            raid_stage_id = self.raid_find_stageid(raid_boss['m_raid_boss_id'], raid_boss['level'])
            if raid_stage_id != 0:
                battle_start_data = self.raid_battle_start(raid_stage_id, raid_boss['id'], party_to_use)
                battle_end_data = self.raid_battle_end_giveup(raid_stage_id, raid_boss['id'])
                boss_count += 1
                self.log(f"Farmed boss with level {raid_boss['level']}. Total bosses farmed: {boss_count}")

    # Will check for raid bosses and will send help requests if active ones are found.
    def raid_check_and_send(self):
        all_bosses = self.raid_get_all_bosses()
        if len(all_bosses) > 0:
            self.log("Number of raid bosses found %d" % len(all_bosses))

        for i in all_bosses:
            if not i['is_discoverer']:
                if i['current_battle_count'] < 1:
                    self.log('There is a shared boss to fight')
                continue
            if not i['is_send_help']:
                sharing_result = self.client.raid_send_help_request(i['id'])
                self.log("Shared boss with %s users" % sharing_result['result']['send_help_count'])
