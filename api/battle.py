import random
from abc import ABCMeta

from api import Player


class Battle(Player, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self.min_rank = 0
        self.min_item_level = 0
        self.min_item_rank = 0
        self.only_weapons = False
        self.auto_rebirth = False

    def autoRebirth(self, i):
        self.auto_rebirth = bool(i)

    def minrank(self, i):
        self.min_rank = int(i)

    def minItemLevel(self, i):
        self.min_item_level = int(i)

    def minItemRank(self, i):
        self.min_item_rank = int(i)

    def onlyWeapons(self, i):
        self.only_weapons = bool(i)

    def battle_status(self):
        data = self.rpc('battle/status', {})
        return data

    def battle_help_list(self):
        data = self.rpc('battle/help_list', {})
        return data

    def battle_start(self, m_stage_id, help_t_player_id, help_t_character_id, act, help_t_character_lv):
        data = self.rpc('battle/start',
                        {"t_character_ids": [], "t_deck_no": self.teamNum(), "m_stage_id": m_stage_id,
                         "m_guest_character_id": 0, "help_t_player_id": help_t_player_id, "t_raid_status_id": 0,
                         "help_t_character_id": help_t_character_id, "auto_rebirth_t_character_ids": [], "act": act,
                         "help_t_character_lv": help_t_character_lv})
        return data

    def battle_start_event(self, m_stage_id, help_t_player_id, help_t_character_id, act, help_t_character_lv):
        data = self.rpc('battle/start',
                        {"t_character_ids": [], "t_deck_no": self.teamNum(), "m_stage_id": m_stage_id,
                         "m_guest_character_id": 0, "help_t_player_id": help_t_player_id, "t_raid_status_id": 0,
                         "help_t_character_id": help_t_character_id, "auto_rebirth_t_character_ids": [], "act": act,
                         "help_t_character_lv": help_t_character_lv})
        return data

    def battle_start_event2(self, m_stage_id, help_t_player_id, help_t_character_id, act, help_t_character_lv):
        data = self.rpc('battle/start',
                        {"t_character_ids": [], "t_deck_no": self.teamNum(), "m_stage_id": m_stage_id,
                         "m_guest_character_id": 0, "help_t_player_id": help_t_player_id, "t_raid_status_id": 0,
                         "help_t_character_id": help_t_character_id, "auto_rebirth_t_character_ids": [], "act": act,
                         "help_t_character_lv": help_t_character_lv})
        return data

    def battle_end(self, battle_exp_data, m_stage_id, battle_type, result, command_count, equipment_id=0,
                   equipment_type=0, m_tower_no=0):
        data = self.rpc('battle/end',
                        {"battle_exp_data": battle_exp_data, "equipment_type": equipment_type, "steal_hl_num": 0,
                         "m_tower_no": m_tower_no, "raid_battle_result": "", "m_stage_id": m_stage_id,
                         "total_receive_damage": 0, "equipment_id": equipment_id, "killed_character_num": 0,
                         "t_raid_status_id": 0, "battle_type": battle_type, "result": result, "innocent_dead_flg": 0,
                         "tower_attack_num": 0, "max_once_damage": int(random.uniform(10000, 10000000) * 10),
                         "mission_status": "1,1,1", "command_count": command_count, "prinny_bomb_num": 0})
        return data

    def getbattle_exp_data(self, start):
        res = []
        for d in start['result']['enemy_list']:
            for r in d:
                res.append(
                    {"finish_member_ids": self.deck, "finish_type": random.choice([1, 2, 3]), "m_enemy_id": d[r]})
        return res

    def battle_story(self, m_stage_id):
        data = self.rpc('battle/story', {"m_stage_id": m_stage_id})
        return data

    def item_world_start(self, equipment_id, equipment_type=1):

        data = self.rpc('item_world/start',
                        {"equipment_type": equipment_type, "t_deck_no": self.teamNum(), "equipment_id": equipment_id,
                         "auto_rebirth_t_character_ids": self.deck if self.auto_rebirth else []})
        return data

    def getDiffWeapon(self, i):
        if not i or 'result' not in i or (
                'after_t_weapon' not in i['result'] and 'after_t_equipment' not in i['result']):
            return False
        stuff = self.weapons if 'after_t_weapon' in i['result'] else self.equipments
        i = i['result']['after_t_weapon' if 'after_t_weapon' in i['result'] else 'after_t_equipment']
        res = [str(i['id'])]
        for k, w in enumerate(stuff):
            if w['id'] == i['id']:
                for j in i:
                    if i[j] != w[j]:
                        s = '%s: %s -> %s' % (j, w[j], i[j])
                        res.append(s)
                stuff[k] = i
        return ', '.join(res)

    def weapon_filter(self, e):
        if self.get_item_rank(e) < self.min_item_rank:
            return False
        if e['lv_max'] < self.min_item_level:
            return False
        if e['lv'] >= e['lv_max']:
            return False
        return True

    def equip_filter(self, e):
        if self.get_item_rank(e) < self.min_item_rank:
            return False
        if e['lv_max'] < self.min_item_level:
            return False
        if e['lv'] >= e['lv_max']:
            return False
        return True

    def tower_start(self, m_tower_no):
        data = self.rpc('tower/start', {"t_deck_no": self.teamNum(), "m_tower_no": m_tower_no})
        return data

    def parseStart(self, start):
        if 'result' in start and 'reward_id' in start['result']:
            reward_id = start['result']['reward_id']
            if start['result']['stage'] in {30, 60, 90, 100}:
                if reward_id == [101, 101, 101, 101, 101, 101, 101, 101, 101, 101, 101, 101, 101, 101, 101]:
                    return 5
                # self.log(reward_id)
                for j, r in enumerate(reward_id):
                    if r == 101:
                        continue
                    equipment_type = start['result']['reward_type'][j]
                    item = self.getWeapon(r) if equipment_type == 3 else self.getEquip(r)
                    rank = self.get_item_rank(item)

                    if item is None:
                        item = {'name': r}
                    self.log(
                        '[+] found item: "%s" with rarity: %s rank: %s' %
                        (item['name'], start['result']['reward_rarity'][j], rank)
                    )

                    # Only farm weapons
                    if self.only_weapons and equipment_type != 3:
                        return 5
                    if hasattr(self, 'min_item_rank') and rank < self.min_rank:
                        return 5
                    if hasattr(self, 'minrare') and start['result']['reward_rarity'][j] < self.minrare:
                        return 5
        return 1
