# -*- coding: utf-8 -*-
import random
import string

from api import BaseAPI


class API(BaseAPI):
    def __init__(self):
        super().__init__()
        self.done = set()

    def config(self, sess: str, uin: str, wait: int = 0, region: int = 1, device: int = 1):
        self.o.sess = sess
        self.o.uin = uin
        self.o.wait = wait
        self.o.set_region(region)
        self.o.set_device(device)

    def get_mail_and_rewards(self):
        self.client.trophy_get_reward_daily()
        for i in range(5):
            self.client.trophy_get_reward()
        for i in range(5):
            self.get_mail()

    def dofarm(self):
        # self.buyRare()
        self.get_mail_and_rewards()
        if True:
            for i in [9, 8, 7, 6, 1012, 1011, 101, 101, 101, 101, 101]:
                self.client.shop_buy_item(itemid=i, quantity=1)

        if True:
            for i in [31, 8, 7, 1, 19, 21, 29, 24, 2, 6, 25, 26]:
                self.client.sub_tutorial_read(m_sub_tutorial_id=i)

        self.completeStory()

    def quick_login(self):
        self.client.login()
        self.player_characters(True)
        self.player_weapons(True)
        # self.player_weapon_effects(True)
        self.player_equipment(True)
        # self.player_equipment_effects(True)
        self.player_items(True)
        self.player_innocents(True)

        data = self.client.player_index()
        if 'result' in data:
            self.o.current_ap = int(data['result']['status']['act'])

        self.player_character_collections()
        self.player_decks()

        self.player_stone_sum()
        self.player_characters(True)

    def dologin(self):
        self.client.login()
        self.client.app_constants()
        self.client.player_tutorial()
        self.client.battle_status()
        # player/profile
        # player/sync
        self.player_characters(True)
        self.player_weapons(True)
        self.client.player_weapon_effects(updated_at=0, page=1)
        self.player_equipment(True)
        self.client.player_equipment_effects(updated_at=0, page=1)
        self.player_items(True)
        self.client.player_clear_stages(updated_at=0, page=1)
        self.client.player_stage_missions(updated_at=0, page=1)
        self.player_innocents(True)
        self.client.player_index()
        self.client.player_agendas()
        self.client.player_boosts()
        self.player_character_collections()
        self.player_decks()
        self.client.friend_index()
        self.client.player_home_customizes()
        self.client.passport_index()
        self.player_stone_sum()
        self.client.player_sub_tutorials()
        self.client.system_version_manage()
        self.client.player_gates()
        self.client.event_index()
        self.client.stage_boost_index()
        self.client.information_popup()
        self.client.player_character_mana_potions()
        self.client.potential_current()
        self.client.potential_conditions()
        self.client.character_boosts()
        self.client.survey_index()
        self.client.kingdom_entries()
        self.client.breeding_center_list()
        self.client.trophy_daily_requests()
        self.client.weapon_equipment_update_effect_unconfirmed()
        self.client.memory_index()
        self.client.battle_skip_parties()
        # boltrend/subscriptions
        self.player_characters(True)

    def addAccount(self):
        self.player_stone_sum()
        self.get_mail()
        self.get_mail()

    def rndAlp(self, n):
        return ''.join([random.choice(string.ascii_lowercase) for x in range(random.randint(n - 1, n))])

    def rndUser(self):
        return self.rndAlp(7).title()

    def get_mail(self):
        did = set()
        while 1:
            ids = self.client.present_index(conditions=[0, 1, 2, 3, 4, 99],
                                            order=1)['result']['_items']
            msgs = []
            for i in ids:
                if i['id'] in did: continue
                msgs.append(i['id'])
                did.add(i['id'])
            if len(msgs) >= 1:
                self.client.present_receive(
                    receive_ids=msgs[0:len(msgs) if len(msgs) <= 20 else 20],
                    conditions=[0, 1, 2, 3, 4, 99],
                    order=1)
            else:
                break

    def doQuest(self, m_stage_id=101102):
        stage = self.gd.get_stage(m_stage_id)
        self.log('doing quest:%s [%s]' % (stage['name'], m_stage_id))
        if stage['exp'] == 0:
            return self.client.battle_story(m_stage_id)

        if stage['act'] > self.current_ap:
            self.log('not enough ap')
            return

        help_players = self.client.battle_help_list()['result']['help_players'][0]
        start = self.client.battle_start(
            m_stage_id=m_stage_id, help_t_player_id=help_players['t_player_id'],
            help_t_character_id=help_players['t_character']['id'], act=stage['act'],
            help_t_character_lv=help_players['t_character']['lv'],
            deck_no=self.o.team_num, deck=self.pd.get_current_deck,
        )
        if 'result' not in start:
            return
        self.client.battle_help_list()
        end = self.client.battle_end(battle_exp_data=self.get_battle_exp_data(start), m_stage_id=m_stage_id,
                                     battle_type=1, result=1)
        res = self.parseReward(end)
        return res

    def upgrade_items(self, ensure_drops: bool = False, only_weapons: bool = False, run_limit: (int, None) = None):

        self.player_innocents(True)
        self.player_weapons(True)
        self.upgrade_item_list(self.pd.weapons, equipment_type=1, ensure_drops=ensure_drops, only_weapons=only_weapons)
        self.player_equipment(True)
        self.upgrade_item_list(self.pd.equipment, equipment_type=2, ensure_drops=ensure_drops,
                               only_weapons=only_weapons)

    def upgrade_item_list(self, items, equipment_type: int, ensure_drops: bool = False, only_weapons: bool = False):
        # items = filter(self.weapon_filter, items)
        for w in filter(self.__item_filter, items):
            self.client.trophy_get_reward_repetition()
            self.get_mail()
            self.log_upgrade_item(w)
            while 1:
                if not self.doItemWorld(
                        equipment_id=w['id'],
                        equipment_type=equipment_type,
                        ensure_drops=ensure_drops,
                        only_weapons=only_weapons
                ):
                    break

    def __item_filter(self, e, i_filter=None):
        if i_filter is None:
            i_filter = {
                'min_item_rank': self.o.min_item_rank,
                'min_item_rarity': self.o.min_item_rarity,
                'min_item_level': self.o.min_item_level,
                'lv_max': False,
            }

        if self.gd.get_item_rank(e) < i_filter['min_item_rank']:
            return False
        if e['rarity_value'] < i_filter['min_item_rarity']:
            return False
        if e['lv_max'] < i_filter['min_item_level']:
            return False
        if i_filter['lv_max'] is False and e['lv'] >= e['lv_max']:
            return False
        return True

    def log_upgrade_item(self, w):
        item = self.gd.get_weapon(w['m_weapon_id']) if 'm_weapon_id' in w else self.gd.get_equipment(
            w['m_equipment_id'])
        self.log(
            '[*] upgrade item: "%s" rarity: %s rank: %s lv: %s lv_max: %s locked: %s' %
            (item['name'], w['rarity_value'], self.gd.get_item_rank(w), w['lv'],
             w['lv_max'], w['lock_flg'])
        )

    def doTower(self, m_tower_no=1):
        start = self.client.tower_start(m_tower_no)
        end = self.client.battle_end(battle_exp_data=self.get_battle_exp_data(start), m_tower_no=m_tower_no,
                                     m_stage_id=0,
                                     battle_type=4, result=1)
        return end

    def doItemWorld(self, equipment_id=None, equipment_type=1, ensure_drops: bool = False, only_weapons: bool = False):
        if equipment_id is None:
            self.log_err('missing equip')
            return
        start = self.client.item_world_start(equipment_id, equipment_type=equipment_type,
                                             deck_no=self.o.team_num,
                                             deck=self.pd.deck(self.o.team_num) if self.o.auto_rebirth else [])

        if start is None or 'result' not in start:
            return False

        result = self.parse_start(start, ensure_drops=ensure_drops, only_weapons=only_weapons)
        end = self.client.battle_end(
            battle_exp_data=self.get_battle_exp_data(start),
            m_stage_id=0,
            result=result,
            battle_type=start['result']['battle_type'],
            equipment_type=start['result']['equipment_type'],
            equipment_id=start['result']['equipment_id'],
        )
        res = self.get_weapon_diff(end)
        if res:
            self.log(res)
        if result == 5:
            self.log('did not drop anything good, retrying..')
            return self.doItemWorld(equipment_id=equipment_id, equipment_type=equipment_type)
        return res

    def getGain(self, t):
        for j in self.pd.items:
            if j['m_item_id'] == t['m_item_id']:
                return t['num'] - j['num']

    def parseReward(self, end):
        drop_result = end
        rpcid = drop_result['id']
        event_points = drop_result['result']['after_t_event']['point'] if drop_result['result']['after_t_event'] else 0
        current_id = drop_result['result']['after_t_stage_current']['current_id']
        drop_result = drop_result['result']['drop_result']
        for e in drop_result:
            if e == 'after_t_item':
                for t in drop_result[e]:
                    i = self.gd.get_item(t['m_item_id'])
                    self.log('%s +%s' % (i['name'], self.getGain(t)))
            elif e == 'drop_character':
                for t in drop_result[e]:
                    self.log('unit:%s lv:%s rarity:%s*' % (
                        self.gd.get_item(t['m_character_id'])['class_name'], t['lv'], t['rarity']))
            elif e == 'stones':
                self.log('+%s nether quartz' % (drop_result[e][0]['num'] - self.pd.gems))
        if event_points > 0:
            self.log('%s event points' % event_points)

        return drop_result

    def getDone(self, page=1):
        if not hasattr(self, 'done'):
            self.done = set()
        r = self.client.player_clear_stages(updated_at=0, page=page)['result']['_items']
        if len(r) <= 0:
            return
        for i in r:
            if i['clear_num'] >= 1:
                self.done.add(i['m_stage_id'])
        return self.getDone(page + 1)

    def getAreaStages(self, m_area_id):
        ss = []
        for s in self.gd.stages:
            if s['m_area_id'] == m_area_id:
                ss.append(s)
        return ss

    def completeStory(self, m_area_id=None, limit=None, farmingAll=False):
        if not farmingAll:
            self.getDone()
        ss = []
        for s in self.gd.stages:
            ss.append(s['id'])
        ss.sort(reverse=False)
        # ss=sorted(ss)
        i = 0
        blacklist = set()
        for s in ss:
            if limit is not None and i >= limit:
                return False
            # print(s,self.getStage(s)['m_area_id'])
            if m_area_id is not None and m_area_id != self.gd.get_stage(s)['m_area_id']:
                continue
            if not farmingAll and s in self.done:
                continue
            if self.gd.get_stage(s)['m_area_id'] in blacklist:
                continue
            try:
                self.doQuest(s)
            except KeyboardInterrupt:
                return False
            except:
                # print(traceback.format_exc())
                self.log('failed %s %s' % (s, self.gd.get_stage(s)['m_area_id']))
                # return False
                blacklist.add(self.gd.get_stage(s)['m_area_id'])
                continue
            self.player_stone_sum()
            self.player_items()
            i += 1

    def useCodes(self):
        for c in ['5uf6dyc6gh', 'dp9GVSSnXG', 'dupj4kjfc3', 'f7wtnxk65h', 'j5zysmkvvv', 'ju56hvdwhz', 'nfefnysyy5',
                  'skfcqwykif', 'sqzvquhtqp', 'tcv5saaskw', 'xnv2ndstwp']:
            self.client.boltrend_exchange_code(c)
        self.get_mail()

# if __name__ == "__main__":
#     a = API()
#     if False:
#         a.password = '26eYVYpYVdbwpPkq'
#         a.uuid = 'e08ed5d9-61a6-4055-a18e-9795d8f40f47'
#         a.dologin()
#     else:
#         a.reroll()
