import base64
import json
import sys
import time

import requests
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from api.constants import Constants
from api.game_data import GameData
from api.logger import Logger
# noinspection PyPep8Naming
from api.options import Options
from boltrend import boltrend
from codedbots import codedbots

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

head = {'version_check': 0, 'signup': 1, 'login': 1, '__rpc': 2}


class Client:
    def __init__(self, variables: Options):
        self.o: Options = variables
        self.c = codedbots()
        self.b = boltrend()
        self.s = requests.Session()
        self.s.verify = False
        self.gd = GameData()
        # self.s.proxies.update({'http': 'http://127.0.0.1:8080','https': 'http://127.0.0.1:8080',})
        # self.set_proxy('127.0.0.1:8080')

    def set_proxy(self, proxy):
        # noinspection HttpUrlsUsage
        tmp = 'http://' + proxy
        self.s.proxies.update({'http': tmp, 'https': tmp})

    def __rpc(self, method: str, prms: dict):
        return self.__call_api(
            'rpc', {
                "rpc": {
                    "jsonrpc": "2.0",
                    "id": self.rndid(),
                    "prms": json.dumps(prms, separators=(',', ':')),
                    "method": method
                }
            })

    def __call_api(self, url: str, data=None):
        if self.o.wait >= 1:
            time.sleep(self.o.wait)

        current_iv = self.c.randomiv()
        self._set_headers(url, current_iv)
        if data is None:
            r = self.s.get(self.o.main_url + url)
        else:
            if data != '':
                cdata = self.c.encrypt(data, current_iv)
            else:
                cdata = data
            r = self.s.post(self.o.main_url + url, data=cdata)
        if 'X-Crypt-Iv' not in r.headers:
            Logger.error('missing iv!')
            exit(1)
            return None
        res = self.c.decrypt(base64.b64encode(r.content), r.headers['X-Crypt-Iv'])
        if 'title' in res and 'Maintenance' in res['title']:
            Logger.info(res['content'])
            exit(1)
        if 'api_error' in res:
            if 'code' in res['api_error'] and res['api_error']['code'] == 30005:
                Logger.info(res['api_error'])
                if self.o.use_potions:
                    rr = self.item_use(use_item_id=301, use_item_num=1)
                    if 'api_error' in rr and rr['api_error']['code'] == 12009:
                        return None
                    return self.__call_api(url, data)
                else:
                    Logger.info('Potion usage disabled. Exiting...')
                    sys.exit()
            else:
                r = data['rpc']['method'] if 'rpc' in data else url
                if 'trophy' not in r:
                    Logger.error('request: "%s" server returned error: %s' % (r, res['api_error']['message']))
                # exit(1)
        if 'password' in res:
            self.o.password = res['password']
            self.o.uuid = res['uuid']
            Logger.info('found password:%s uuid:%s' % (self.o.password, self.o.uuid))
        if 'result' in res and 'newest_resource_version' in res['result']:
            self.o.newest_resource_version = res['result']['newest_resource_version']
            Logger.info('found resouce:%s' % self.o.newest_resource_version)
        if 'fuji_key' in res:
            if sys.version_info >= (3, 0):
                self.c.key = bytes(res['fuji_key'], encoding='utf8')
            else:
                self.c.key = bytes(res['fuji_key'])
            self.o.session_id = res['session_id']
            Logger.info('found fuji_key:%s' % self.c.key)
        if 'result' in res and 't_player_id' in res['result']:
            if 'player_rank' in res['result']:
                Logger.info(
                    't_player_id:%s player_rank:%s' % (res['result']['t_player_id'], res['result']['player_rank']))
            self.o.pid = res['result']['t_player_id']
        if 'result' in res and 'after_t_status' in res['result']:
            self.o.current_ap = int(res['result']['after_t_status']['act'])
            Logger.info('%s / %s rank:%s' % (
                res['result']['after_t_status']['act'], res['result']['after_t_status']['act_max'],
                res['result']['after_t_status']['rank']))
        if 'result' in res and 't_innocent_id' in res['result']:
            if res['result']['t_innocent_id'] != 0:
                Logger.info('t_innocent_id:%s' % (res['result']['t_innocent_id']))
                status = 0
                while status == 0:
                    status = self.item_world_persuasion()
                    Logger.info('status:%s' % status)
                    status = status['result']['after_t_innocent']['status']
        return res

    def _set_headers(self, url: str, iv: str):
        i = head[url] if url in head else None
        self.s.headers.clear()

        if i == 0:
            if self.o.region == 2:
                self.s.headers.update({
                    'X-Unity-Version': '2018.4.3f1',
                    'Accept-Language': 'en-us',
                    'X_CHANNEL': '1',
                    'Content-Type': 'application/x-haut-hoiski',
                    'User-Agent': 'en/17 CFNetwork/1206 Darwin/20.1.0',
                    'X-OS-TYPE': '1',
                    'X-APP-VERSION': self.o.version,
                    'X-Crypt-Iv': iv,
                    'Accept': '*/*'
                })
            else:
                self.s.headers.update({
                    'X-PERF-SCENE-TIME': '8619',
                    'X-PERF-APP-BUILD-NUMBER': '0',
                    'X-PERF-NETWORK-REQ-LAST': '1',
                    'X-PERF-DISC-FREE': '5395',
                    'X-PERF-FPS-LAST-MED': '59.99',
                    'X-APP-VERSION': self.o.version,
                    'X-PERF-OS-VERSION': 'iOS 14.2',
                    'X-PERF-CPU-SYS': '0',
                    'X-PERF-CPU-USER': '40.79',
                    'X-PERF-BUTTERY': '100',
                    'X-PERF-SCENE-TRACE':
                        'startup_scene,title_scene,startup_scene,title_scene',
                    'X-PERF-NETWORK-ERR-LAST': '0',
                    'X-PERF-NETWORK-REQ-TOTAL': '1',
                    'X-PERF-CPU-IDLE': '59.21',
                    'X-PERF-APP-VERSION': '2.11.2',
                    'X-PERF-FPS-LAST-AVG': '59.23',
                    'User-Agent':
                        'forwardworks/194 CFNetwork/1206 Darwin/20.1.0',
                    'X-PERF-MEM-USER': '1624',
                    'X-PERF-LAUNCH-TIME': '20210408T15:50:36Z',
                    'X-PERF-SCENE': 'title_scene',
                    'X-PERF-FPS': '59.99',
                    'X-Crypt-Iv': iv,
                    'X-PERF-MEM-AVAILABLE': '24',
                    'X-OS-TYPE': str(self.o.device),
                    'X-PERF-LAST-DELTA-TIMES': '16,17,16,17,21,13,16,17,17,17',
                    'X-PERF-NETWORK-ERR-TOTAL': '0',
                    'X-PERF-DEVICE': 'iPad7,5',
                    'Content-Type': 'application/x-haut-hoiski',
                    'X-PERF-OS': 'iOS 14.2',
                    'X-PERF-MEM-PYSIC': '1981',
                    'X-Unity-Version': '2018.4.20f1',
                    'X-PERF-TIME': '20210408T15:52:43Z',
                    'X-PERF-APP-ID': 'com.disgaearpg.forwardworks',
                    'X-PERF-LAUNCH-DURATION': '70363'
                })
        elif i == 1:
            if self.o.region == 2:
                self.s.headers.update({
                    'X-Unity-Version': '2018.4.3f1',
                    'X-Crypt-Iv': iv,
                    'Accept-Language': 'en-us',
                    'X_CHANNEL': '1',
                    'Content-Type': 'application/x-haut-hoiski',
                    'User-Agent': 'en/17 CFNetwork/1206 Darwin/20.1.0',
                    'X-OS-TYPE': '1',
                    'X-APP-VERSION': self.o.version
                })
            else:
                self.s.headers.update({
                    'X-Unity-Version': '2018.4.20f1',
                    'X-Crypt-Iv': iv,
                    'Accept-Language': 'en-us',
                    'Content-Type': 'application/x-haut-hoiski',
                    'User-Agent':
                        'forwardworks/194 CFNetwork/1206 Darwin/20.1.0',
                    'X-OS-TYPE': str(self.o.device),
                    'X-APP-VERSION': self.o.version
                })
        elif i == 2:
            self.s.headers.update({
                'X-Unity-Version': '2018.4.20f1',
                'X-Crypt-Iv': iv,
                'Accept-Language': 'en-us',
                'Content-Type': 'application/x-haut-hoiski',
                'User-Agent': 'iPad6Gen/iOS 14.2',
                'X-OS-TYPE': str(self.o.device),
                'X-APP-VERSION': self.o.version,
                'X-SESSION': self.o.session_id
            })
        else:
            self.s.headers.update({
                'X-Unity-Version': '2018.4.20f1',
                'X-Crypt-Iv': iv,
                'Accept-Language': 'en-us',
                'Content-Type': 'application/x-haut-hoiski',
                'User-Agent': 'forwardworks/194 CFNetwork/1206 Darwin/20.1.0',
                'X-OS-TYPE': str(self.o.device),
                'X-APP-VERSION': self.o.version
            })

    # noinspection SpellCheckingInspection
    def rndid(self):
        return self.c.rndid()

    def login(self):
        if self.o.region == 1 or hasattr(self, 'isReroll'):
            data = self.__call_api('login', {
                "password": self.o.password,
                "uuid": self.o.uuid
            })
        else:
            data = self.__call_api(
                'sdk/login', {
                    "platform": self.o.platform,
                    "sess": self.o.sess,
                    "sdk": "BC4D6C8AE94230CC",
                    "region": "non_mainland",
                    "uin": self.o.uin
                })
        return data

    # Start API CALLS
    ####################

    #################
    # Trophy Endpoints
    #################

    def trophy_get_reward_daily(self, receive_all: int = 1, _id: int = 0):
        return self.__rpc('trophy/get_reward_daily', {"receive_all": receive_all, "id": _id})

    def trophy_get_reward(self, receive_all: int = 1, _id: int = 0):
        return self.__rpc('trophy/get_reward', {"receive_all": receive_all, "id": _id})

    def trophy_get_reward_repetition(self, receive_all: int = 1, _id: int = 0):
        return self.__rpc('trophy/get_reward_repetition', {"receive_all": receive_all, "id": _id})

    def trophy_daily_requests(self):
        return self.__rpc('trophy/daily_requests', {})

    def trophy_character_missions(self, m_character_ids, updated_at):
        return self.__rpc('trophy/character_missions', {"m_character_ids": m_character_ids, "updated_at": updated_at})

    # Get rewards from etna resorts
    def trophy_get_reward_daily_request(self):
        # trophy/get_reward_daily_request
        return self.__rpc("trophy/get_reward_daily_request", {'receive_all': 1, 'id': 0})

    def trophy_beginner_missions(self, sheet_type=None):
        return self.__rpc('trophy/beginner_missions', {} if sheet_type is None else {'sheet_type': sheet_type})

    #################
    # Battle Endpoints
    #################

    def battle_status(self):
        return self.__rpc('battle/status', {})

    def battle_help_list(self):
        return self.__rpc('battle/help_list', {})

    def battle_skip_parties(self):
        return self.__rpc('battle/skip_parties', {})

    def battle_start(self, m_stage_id, help_t_player_id=None, help_t_character_id=0, act=0, help_t_character_lv=0,
                     deck_no=1, deck=None, raid_status_id=0):
        if help_t_player_id is None:
            help_t_player_id = []
        if deck is None:
            deck = []
        return self.__rpc('battle/start',
                          {"t_character_ids": [], "t_deck_no": deck_no, "m_stage_id": m_stage_id,
                           "m_guest_character_id": 0, "help_t_player_id": help_t_player_id,
                           "t_raid_status_id": raid_status_id,
                           "auto_rebirth_t_character_ids": deck, "act": act,
                           "help_t_character_id": help_t_character_id,
                           "help_t_character_lv": help_t_character_lv})

    def battle_end(self, m_stage_id, battle_type, result=0, battle_exp_data=[], equipment_id: int = 0,
                   equipment_type: int = 0, m_tower_no: int = 0, raid_status_id: int = 0, raid_battle_result: str = '',
                   skip_party_update_flg: bool = True, common_battle_result=None):

        if common_battle_result is None:
            common_battle_result = self.o.common_battle_result

        if raid_battle_result != '':
            return self.__rpc('battle/end', {
                "m_stage_id": m_stage_id,
                "m_tower_no": m_tower_no,
                "equipment_id": equipment_id,
                "equipment_type": equipment_type,
                "innocent_dead_flg": 0,
                "t_raid_status_id": raid_status_id,
                "raid_battle_result": raid_battle_result,
                "m_character_id": 0,
                "division_battle_result": "",
                "battle_type": battle_type,
                "result": result,
                "battle_exp_data": battle_exp_data,
                "common_battle_result": common_battle_result,
                "skip_party_update_flg": skip_party_update_flg,
            })
        else:
            return self.__rpc('battle/end', {
                "battle_exp_data": battle_exp_data,
                "equipment_type": equipment_type,
                "m_tower_no": m_tower_no,
                "raid_battle_result": raid_battle_result,
                "m_stage_id": m_stage_id,
                "equipment_id": equipment_id,
                "t_raid_status_id": 0,
                "battle_type": battle_type,
                "result": result,
                "innocent_dead_flg": 0,
                "skip_party_update_flg": skip_party_update_flg,
                "common_battle_result": common_battle_result,
            })

    def battle_story(self, m_stage_id):
        return self.__rpc('battle/story', {"m_stage_id": m_stage_id})

    def axel_context_battle_end(self, m_character_id, battle_exp_data, common_battle_result: str = ''):
        return self.__rpc('battle/end', {
            "m_stage_id": 0,
            "m_tower_no": 0,
            "equipment_id": 0,
            "equipment_type": 0,
            "innocent_dead_flg": 0,
            "t_raid_status_id": 0,
            "raid_battle_result": "",
            "m_character_id": m_character_id,
            "division_battle_result": "",
            "battle_type": 7,
            "result": 1,
            "battle_exp_data": battle_exp_data,
            "common_battle_result": common_battle_result,
            "skip_party_update_flg": True
        })

    def battle_skip(self, m_stage_id, deck_no: int, skip_number: int, helper_player, deck=None):
        if deck is None:
            deck = []

        stage = self.gd.get_stage(m_stage_id)
        return self.__rpc('battle/skip', {
            "m_stage_id": m_stage_id,
            "help_t_player_id": helper_player['t_player_id'],
            "help_t_character_id": helper_player['t_character']['id'],
            "help_t_character_lv": helper_player['t_character']['lv'],
            "t_deck_no": deck_no,
            "m_guest_character_id": 0,
            "t_character_ids": [],
            "skip_num": skip_number,
            "battle_type": 3,  # needs to be tested. It was an exp gate
            "act": stage['act'] * skip_number,
            "auto_rebirth_t_character_ids": deck,
            "t_memery_ids": []  # pass parameters?
        })

    def battle_skip_stages(self, m_stage_ids, deck_no: int, skip_number: int, helper_player, deck=None):
        if deck is None:
            deck = []

        # calculate ap usage. Every stage is skipped 3 times
        act = 0
        for m_stage_id in m_stage_ids:
            stage = self.gd.get_stage(m_stage_id)
            act = act + (stage['act'] * skip_number)

        return self.__rpc('battle/skip_stages', {
            "m_stage_id": 0,
            "help_t_player_id": helper_player['t_player_id'],
            "help_t_character_id": helper_player['t_character']['id'],
            "help_t_character_lv": helper_player['t_character']['lv'],
            "t_deck_no": deck_no,
            "m_guest_character_id": 0,
            "t_character_ids": [],
            "skip_num": 0,
            "battle_type": 3,  # needs to be tested. It was an exp gate
            "act": act,
            "auto_rebirth_t_character_ids": deck,
            "t_memery_ids": [],  # pass parameters?
            "m_stage_ids": m_stage_ids
        })

    #################
    # Raid Endpoints
    #################

    def raid_send_help_request(self, raid_id):
        return self.__rpc('raid/help', {"t_raid_status_id": raid_id})

    def raid_index(self):
        return self.__rpc('raid/index', {})

    def raid_ranking_reward(self):
        return self.__rpc('raid/ranking_reward', {})

    def raid_give_up_boss(self, t_raid_status_id):
        return self.__rpc('raid/give_up', {"t_raid_status_id": t_raid_status_id})

    def raid_current(self):
        return self.__rpc('raid/current', {})

    def raid_history(self, raidID=Constants.Current_Raid_ID):
        return self.__rpc('raid/history', {"m_event_id": raidID})

    # reward for a specific boss battle
    def raid_reward(self, t_raid_status_id):
        return self.__rpc('raid/reward', {"t_raid_status_id": t_raid_status_id})

    def raid_gacha(self, m_event_gacha_id, lottery_num):
        return self.__rpc('event/gacha_do', {"m_event_gacha_id": m_event_gacha_id, "lottery_num": lottery_num})

    def raid_update(self, m_raid_boss_id, step):
        return self.__rpc('raid_boss/update', {"m_raid_boss_id": m_raid_boss_id, "step": step})

    #################
    # Gacha Endpoints
    #################

    def gacha_available(self):
        return self.__rpc('gacha/available', {})

    def gacha_do(self, is_gacha_free, price, item_type, num, m_gacha_id, item_id):
        return self.__rpc('gacha/do',
                          {"is_gacha_free": is_gacha_free, "price": price, "item_type": item_type, "num": num,
                           "m_gacha_id": m_gacha_id, "item_id": item_id})

    def gacha_sums(self):
        return self.__rpc('gacha/sums', {})

    #################
    # Player Endpoints
    #################

    def player_sync(self):
        return self.__rpc('player/sync', {})

    def player_tutorial_gacha_single(self):
        return self.__rpc('player/tutorial_gacha_single', {})

    def player_tutorial_choice_characters(self):
        return self.__rpc('player/tutorial_choice_characters', {})

    def player_characters(self, updated_at: int = 0, page: int = 1):
        return self.__rpc('player/characters', {
            "updated_at": updated_at,
            "page": page
        })

    def player_character_collections(self):
        return self.__rpc('player/character_collections', {})

    def player_weapons(self, updated_at: int = 0, page: int = 1):
        return self.__rpc('player/weapons', {
            "updated_at": updated_at,
            "page": page
        })

    def player_weapon_effects(self, updated_at: int = 0, page: int = 1):
        return self.__rpc('player/weapon_effects', {"updated_at": updated_at, "page": page})

    def player_equipments(self, updated_at: int = 0, page: int = 1):
        return self.__rpc('player/equipments', {
            "updated_at": updated_at,
            "page": page
        })

    def player_equipment_effects(self, updated_at: int = 0, page: int = 1):
        return self.__rpc('player/equipment_effects', {"updated_at": updated_at, "page": page})

    def player_innocents(self, updated_at: int = 0, page: int = 1):
        return self.__rpc('player/innocents', {"updated_at": updated_at, "page": page})

    def player_clear_stages(self, updated_at: int = 0, page: int = 1):
        return self.__rpc('player/clear_stages', {"updated_at": updated_at, "page": page})

    def player_stage_missions(self, updated_at: int, page: int):
        return self.__rpc('player/stage_missions', {"updated_at": updated_at, "page": page})

    def player_index(self):
        return self.__rpc('player/index', {})

    def player_agendas(self):
        return self.__rpc('player/agendas', {})

    def player_boosts(self):
        return self.__rpc('player/boosts', {})

    def player_decks(self):
        return self.__rpc('player/decks', {})

    def player_home_customizes(self):
        return self.__rpc('player/home_customizes', {})

    def player_items(self, updated_at: int = 0, page: int = 1):
        return self.__rpc('player/items', {"updated_at": updated_at, "page": page})

    def player_stone_sum(self):
        return self.__rpc('player/stone_sum', {})

    def player_sub_tutorials(self):
        return self.__rpc('player/sub_tutorials', {})

    def player_gates(self):
        return self.__rpc('player/gates', {})

    def player_character_mana_potions(self):
        return self.__rpc('player/character_mana_potions', {})

    def player_tutorial(self, chara_id_list=None, step=None, chara_rarity_list=None, name=None, gacha_fix=None):
        if chara_id_list is None:
            data = self.__rpc('player/tutorial', {})
        else:
            data = self.__rpc('player/tutorial',
                              {"charaIdList": chara_id_list, "step": step, "charaRarityList": chara_rarity_list,
                               "name": name, "gacha_fix": gacha_fix})
        return data

    def player_update_device_token(self, device_token: str = ''):
        return self.__rpc('player/update_device_token',
                          {"device_token": device_token})

    def player_add(self):
        return self.__rpc('player/add', {})

    def player_badge_homes(self):
        return self.__rpc('player/badge_homes', {})

    def player_badges(self):
        return self.__rpc('player/badges', {})

    def player_update_equip_detail(self, e: dict, innocents: list[int] = []):
        equip_type = 1 if 'm_weapon_id' in e else 2
        return self.__rpc("player/update_equip_detail", {
            't_equip_id': e['id'],
            'equip_type': equip_type,
            'lock_flg': e['lock_flg'],
            'innocent_auto_obey_flg': e['innocent_auto_obey_flg'],
            'change_innocent_list': innocents
        })

    #################
    # Kingdom Endpoints
    #################

    def kingdom_entries(self):
        return self.__rpc('kingdom/entries', {})

    def kingdom_weapon_equipment_entry(self, weap_ids: list[int] = [], equip_ids: list[int] = []):
        return self.__rpc("kingdom/weapon_equipment_entry", {'t_weapon_ids': weap_ids, 't_equipment_ids': equip_ids})

    def kingdom_innocent_entry(self, innocent_ids: list[int] = []):
        return self.__rpc("kingdom/innocent_entry", {'t_innocent_ids': innocent_ids})

    def etna_resort_refine(self, item_type, _id):
        return self.__rpc('weapon_equipment/rarity_up', {"item_type": item_type, "id": _id})

    #################
    # Shop Endpoints
    #################

    def shop_equipment_items(self):
        return self.__rpc('shop/equipment_items', {})

    def shop_equipment_shop(self):
        return self.__rpc('shop/equipment_shop', {})

    def shop_buy_equipment(self, item_type: int, itemid: list[int]):
        return self.__rpc('shop/buy_equipment', {"item_type": item_type, "ids": [itemid]})

    def shop_buy_item(self, itemid: int, quantity: int):
        return self.__rpc('shop/buy_item', {"id": itemid, "quantity": quantity})

    def shop_sell_equipment(self, sell_equipments):
        return self.__rpc('shop/sell_equipment', {"sell_equipments": sell_equipments})

    def shop_change_equipment_items(self, shop_rank: int = 32):
        update_number = self.shop_equipment_shop()['result']['lineup_update_num']
        if update_number < 5:
            data = self.__rpc('shop/change_equipment_items', {"shop_rank": shop_rank})
        else:
            Logger.warn('Free refreshes used up already')
            data = {}
        return data

    def shop_gacha(self):
        return self.__rpc('shop/garapon', {"m_garapon_id": 1})

    def shop_index(self):
        return self.__rpc('shop/index', {})

    #################
    # Friend Endpoints
    #################

    def friend_index(self):
        return self.__rpc('friend/index', {})

    def friend_send_act(self, target_t_player_id: int = 0):
        return self.__rpc('friend/send_act', {"target_t_player_id": target_t_player_id})

    def friend_receive_act(self, target_t_player_id: int = 0):
        return self.__rpc('friend/receive_act', {"target_t_player_id": target_t_player_id})

    def friend_send_sardines(self):
        data = self.__rpc('friend/send_act', {"target_t_player_id": 0})
        if data['error'] == 'You cannot send more sardine.':
            return data['error']
        Logger.info(f"Sent sardines to {data['result']['send_count_total']} friends")

    #################
    # Bingo Endpoints
    #################

    def bingo_index(self, bingo_id=Constants.Current_Bingo_ID):
        return self.__rpc('bingo/index', {"id": bingo_id})

    def bingo_lottery(self, bingo_id=Constants.Current_Bingo_ID, use_stone=False):
        return self.__rpc('bingo/lottery', {"id": bingo_id, "use_stone": use_stone})

    # ids takes an array like [57]
    def bingo_receive_reward(self, reward_id):
        return self.__rpc('bingo/receive', {"ids": reward_id})

    #################
    # Breeding Center Endpoints
    #################

    def breeding_center_list(self):
        return self.__rpc('breeding_center/list', {})

    # takes arrays with ids for weapons and equips to retrieve from ER Deposit
    def breeding_center_pick_up(self, t_weapon_ids, t_equipment_ids):
        return self.__rpc('breeding_center/pick_up', {"t_weapon_ids": t_weapon_ids, "t_equipment_ids": t_equipment_ids})

    # takes arrays with ids for weapons and equips to add to ER Deposit
    def breeding_center_entrust(self, t_weapon_ids, t_equipment_ids):
        return self.__rpc('breeding_center/entrust', {"t_weapon_ids": t_weapon_ids, "t_equipment_ids": t_equipment_ids})

    #################
    # Misc Endpoints
    #################

    def survey_index(self):
        return self.__rpc('survey/index', {})

    def survey_start(self, m_survey_id, hour, t_character_ids, auto_rebirth_t_character_ids=[]):
        return self.__rpc('survey/start', {"m_survey_id": m_survey_id, "hour": hour, "t_character_ids": t_character_ids,
                                           "auto_rebirth_t_character_ids": auto_rebirth_t_character_ids})

    def survey_end(self, m_survey_id, cancel):
        return self.__rpc('survey/end', {"m_survey_id": m_survey_id, "cancel": cancel})

    # bribe data [{"m_item_id":401,"num":4}]
    def survey_use_bribe_item(self, m_survey_id, bribe_data):
        return self.__rpc('survey/use_bribe_item', {"m_survey_id": m_survey_id, "bribe_data": bribe_data})

    #################
    # Misc Endpoints
    #################

    def login_update(self):
        return self.__rpc('login/update', {})

    def version_check(self):
        return self.__call_api('version_check', None)

    def signup(self):
        return self.__call_api('signup', '')

    def passport_index(self):
        return self.__rpc('passport/index', {})

    def sub_tutorial_read(self, m_sub_tutorial_id: int):
        return self.__rpc('sub_tutorial/read', {"m_sub_tutorial_id": m_sub_tutorial_id})

    def boltrend_exchange_code(self, code: str):
        return self.__rpc('boltrend/exchange_code', {"code": code})

    def app_constants(self):
        return self.__rpc('app/constants', {})

    def system_version_manage(self):
        return self.__rpc('system/version_manage', {})

    def present_history(self):
        return self.__rpc('present/history', {})

    def present_index(self, is_limit_notice=None, conditions=None, order=None):
        if is_limit_notice is not None:
            data = self.__rpc('present/index', {"is_limit_notice": is_limit_notice})
        else:
            data = self.__rpc('present/index', {"conditions": conditions, "order": order})
        return data

    def present_receive(self, receive_ids, conditions, order):
        return self.__rpc('present/receive', {"receive_ids": receive_ids, "conditions": conditions, "order": order})

    def adjust_add(self, event_id: int):
        return self.__rpc('adjust/add', {"event_id": event_id})

    def event_index(self, event_ids=None):
        if event_ids is None:
            return self.__rpc('event/index', {})
        else:
            return self.__rpc('event/index', {"m_event_ids": event_ids})

    def stage_boost_index(self):
        return self.__rpc('stage_boost/index', {})

    def information_popup(self):
        return self.__rpc('information/popup', {})

    def potential_current(self):
        return self.__rpc('potential/current', {})

    def potential_conditions(self):
        return self.__rpc('potential/conditions', {})

    def character_boosts(self):
        return self.__rpc('character/boosts', {})

    def update_admin_flg(self):
        return self.__rpc('debug/update_admin_flg', {})

    def weapon_equipment_update_effect_unconfirmed(self):
        return self.__rpc('weapon_equipment/update_effect_unconfirmed', {})

    def system_version_update(self):
        return self.__rpc('system/version_update', {
            "app_version": self.o.version,
            "resouce_version": self.o.newest_resource_version,
            "database_version": "0"
        })

    def memory_index(self):
        return self.__rpc('memory/index', {})

    def item_world_persuasion(self):
        return self.__rpc('item_world/persuasion', {})

    def item_world_start(self, equipment_id: int, equipment_type: int, deck_no: int, deck=None):
        if deck is None:
            deck = []

        return self.__rpc('item_world/start', {
            "equipment_type": equipment_type,
            "t_deck_no": deck_no,
            "equipment_id": equipment_id,
            "auto_rebirth_t_character_ids": deck,
        })

    def item_use(self, use_item_id: int, use_item_num: int):
        return self.__rpc('item/use', {"use_item_id": use_item_id, "use_item_num": use_item_num})

    def tower_start(self, m_tower_no: int, deck_no: int):
        return self.__rpc('tower/start', {"t_deck_no": deck_no, "m_tower_no": m_tower_no})

    def axel_context_battle_start(self, act, m_character_id: int, t_character_ids):
        return self.__rpc('character_contest/start',
                          {"act": act, "m_character_id": m_character_id, "t_character_ids": t_character_ids})

    def innocent_remove_all(self, ids, cost: int = 0):
        return self.__rpc("innocent/remove_all", {"t_innocent_ids": ids, "cost": cost})

    def innocent_training(self, t_innocent_id):
        return self.__rpc('innocent/training', {"t_innocent_id": t_innocent_id})

    def hospital_index(self):
        return self.__rpc('hospital/index', {})

    def hospital_roulette(self):
        data = self.__rpc('hospital/roulette', {})
        if data['error'] == 'Not the time to recover':
            return data['error']
        Logger.info(f"Hospital Roulettte - Recovered {data['result']['recovery_num']} AP")
        return data
