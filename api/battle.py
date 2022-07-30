import random
import time
from abc import ABCMeta

from api.player import Player


class Battle(Player, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    def battle_help_get_friend_by_id(self, help_t_player_id):
        friend = None
        self.log("Looking for friend")
        while friend is None:
            help_players = self.client.battle_help_list()['result']['help_players']
            friend = next((x for x in help_players if x['t_player_id'] == help_t_player_id), None)
            time.sleep(1)
        return friend

    def battle_skip(self, m_stage_id, skip_number, help_t_player_id: int = 0):

        if help_t_player_id == 0:
            helper_player = self.client.battle_help_list()['result']['help_players'][0]
        else:
            helper_player = self.battle_help_get_friend_by_id(help_t_player_id)

        return self.client.battle_skip(m_stage_id=m_stage_id, deck_no=self.o.team_num, skip_number=skip_number,
                                       helper_player=helper_player, deck=self.pd.deck())

    # m_stage_ids [5010711,5010712,5010713,5010714,5010715] for monster reincarnation
    def battle_skip_stages(self, m_stage_ids, help_t_player_id=0):
        if help_t_player_id == 0:
            helper_player = self.client.battle_help_list()['result']['help_players'][0]
        else:
            helper_player = self.battle_help_get_friend_by_id(help_t_player_id)

        return self.client.battle_skip_stages(
            m_stage_ids=m_stage_ids, helper_player=helper_player,
            deck_no=self.o.team_num, deck=self.pd.deck(self.o.team_num), skip_number=3,
        )

    def get_battle_exp_data(self, start):
        res = []
        for d in start['result']['enemy_list']:
            for r in d:
                res.append({
                    "finish_member_ids": self.pd.deck(start['result']['t_deck_no']),
                    "finish_type": random.choice([1, 2, 3]),
                    "m_enemy_id": d[r]
                })
        return res

    def do_tower(self, m_tower_no=1):
        start = self.client.tower_start(m_tower_no)
        end = self.client.battle_end(battle_exp_data=self.get_battle_exp_data(start),
                                     m_tower_no=m_tower_no,
                                     m_stage_id=0,
                                     battle_type=4,
                                     result=1)
        return end

    def parse_start(self, start, ensure_drops: bool = False, only_weapons: bool = False):
        if 'result' in start and 'reward_id' in start['result']:
            reward_id = start['result']['reward_id'][10]
            reward_type = start['result']['reward_type'][10]
            reward_rarity = start['result']['reward_rarity'][10]

            # stage with no drops or ensure_drops is false, continue
            if start['result']['stage'] % 10 != 0 or not ensure_drops:
                return 1

            # no drop, ensuring drops, retry
            if reward_id == 101:
                return 5

            # drop, no Item General/King/God stage, continue
            if start['result']['stage'] not in {30, 60, 90, 100}:
                return 1
            # drop, rarity less than min_rarity, retry
            if reward_rarity < self.o.min_rarity:
                return 5
            # equipment drop, but farming only weapons, retry
            if reward_type == 4 and only_weapons:
                return 5
            item = self.gd.get_weapon(reward_id) if reward_type == 3 else self.gd.get_equipment(reward_id)

            # drop, rank less than min_rank, retry
            if self.gd.get_item_rank(item) < self.o.min_rank:
                return 5

            if item is None:
                item = {'name': ''}

            self.log('[+] found item:%s with rarity:%s' % (item['name'], reward_rarity))
            return 1
        else:
            return 1
