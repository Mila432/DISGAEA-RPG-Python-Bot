# -*- coding: utf-8 -*-
import requests
import base64
import time
import string
import random
import json
import sys
from api.constants import Constants
from api.raid import Raid
from codedbots import codedbots
from db import Database
import db2
from boltrend import boltrend
from contextlib import suppress

from api import BaseAPI

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from data import data as gamedata

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

head = {'version_check': 0, 'signup': 1, 'login': 1, 'rpc': 2}


class API(BaseAPI):

    def __init__(self):
        super().__init__()
        self.c = codedbots()
        self.db = Database()
        self.b = boltrend()
        self.s = requests.Session()
        self.s.verify = False
        self.setRegion(1)
        #self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'http://127.0.0.1:8888',})
        self.setDevice(1)
        self.setReincarnationIDs([])
        self.setActiveParty(1)
        self.UsePotions = True
        self.EnsureDrops = False
        self.GetOnlyWeapons = False
        self.minrare = 0

    def setProxy(self, proxy):
        proxy = 'http://' + proxy
        proxy = {
            'http': proxy,
            'https': proxy,
        }
        self.s.proxies.update(proxy)

    def setRegion(self, r):
        if r == 1:
            self.mainurl = 'https://api.rpg.disgaea-app.com/'
            self.version = '2.11.2'
            self.region = 1
        else:
            self.mainurl = 'https://disgaea-game-live-en.boltrend.com/'
            self.version = '1.0.254'
            self.region = 2

    def setDevice(self, r):
        self.device = str(r)
        if self.device == '1':
            self.platform = 'iOS'
        else:
            self.platform = 'Android'

    def wait(self, n):
        self.waitn = int(n)

    def setReincarnationIDs(self, ids):
        self.reincarnationIDs = ids

    def setActiveParty(self, activeParty):
        self.activeParty = activeParty
        self.reincarnationIDs = []
        if activeParty != 1:
            self.player_decks()

    def disablePotionUsage(self):
        self.UsePotions = False

    def minrarity(self, i):
        self.minrare = int(i)

    def setPassword(self, p):
        self.password = p

    def setUUID(self, p):
        self.uuid = p

    def setSDK(self, p):
        self.sdk = p

    def log(self, msg):
        if sys.version_info >= (3, 0):
            print('[%s] %s' %
                  (time.strftime('%H:%M:%S'),
                   msg))  #.encode('utf-8').encode('ascii', 'ignore')))
        else:
            print('[%s] %s' % (time.strftime('%H:%M:%S'), msg.encode('utf-8')))

    def callAPI(self, url, data=None):
        if hasattr(self, 'waitn') and self.waitn >= 1:
            time.sleep(self.waitn)
        self.thisiv = self.c.randomiv()
        #self.thisiv = b'r66Ao6sZctBEia5y0QH/FQ=='
        self.setheaders(url)
        if data is None:
            r = self.s.get(self.mainurl + url)
        else:
            if data != '':
                cdata = self.c.encrypt(data, self.thisiv)
                #cdata = base64.b64encode(json.dumps(data).encode())
            else:
                cdata = data

            r = self.s.post(self.mainurl + url, data=cdata)
        if 'X-Crypt-Iv' not in r.headers:
            self.log('missing iv!')
            return None
            
        res = self.c.decrypt(base64.b64encode(r.content), r.headers['X-Crypt-Iv'])
        if 'title' in res and 'Maintenance' in res['title']:
            self.log(res['content'])
            exit(1)
        if 'api_error' in res:
            if 'code' in res['api_error'] and res['api_error']['code'] == 30005:
                self.log(res['api_error'])
                if (self.UsePotions):
                    rr = self.item_use(use_item_id=301, use_item_num=1)
                    if 'api_error' in rr and rr['api_error']['code'] == 12009:
                        return None
                    return self.callAPI(url, data)
                else:
                    self.log('Potion usage disabled. Exiting...')
                    sys.exit()
            else:
                self.log('server returned error: %s' %
                         (res['api_error']['message']))
                #exit(1)
        if 'password' in res:
            self.password = res['password']
            self.uuid = res['uuid']
            self.log('found password:%s uuid:%s' % (self.password, self.uuid))
        if 'result' in res and 'newest_resource_version' in res['result']:
            self.newest_resource_version = res['result'][
                'newest_resource_version']
            self.log('found resouce:%s' % (self.newest_resource_version))
        if 'fuji_key' in res:
            if sys.version_info >= (3, 0):
                self.c.key = bytes(res['fuji_key'], encoding='utf8')
            else:
                self.c.key = bytes(res['fuji_key'])
            self.session_id = res['session_id']
            self.log('found fuji_key:%s' % (self.c.key))
        if 'result' in res and 't_player_id' in res['result']:
            if 'player_rank' in res['result']:
                self.log('t_player_id:%s player_rank:%s' %
                         (res['result']['t_player_id'],
                          res['result']['player_rank']))
            self.pid = res['result']['t_player_id']
        if 'result' in res and 'after_t_status' in res['result']:
            self.log('%s / %s rank:%s' %
                     (res['result']['after_t_status']['act'],
                      res['result']['after_t_status']['act_max'],
                      res['result']['after_t_status']['rank']))
        if 'result' in res and 't_innocent_id' in res['result']:
            if res['result']['t_innocent_id'] != 0:
                self.log('t_innocent_id:%s' % (res['result']['t_innocent_id']))
                status = 0
                while (status == 0):
                    status = self.item_world_persuasion()
                    self.log('status:%s' % (status))
                    status = status['result']['after_t_innocent']['status']
        return res

    def setheaders(self, i):
        try:
            i = head[i]
        except:
            i = None
        self.s.headers.clear()
        if i == 0:
            if self.region == 2:
                self.s.headers.update({
                    'X-Unity-Version': '2018.4.3f1',
                    'Accept-Language': 'en-us',
                    'X_CHANNEL': '1',
                    'Content-Type': 'application/x-haut-hoiski',
                    'User-Agent': 'en/17 CFNetwork/1206 Darwin/20.1.0',
                    'X-OS-TYPE': '1',
                    'X-APP-VERSION': self.version,
                    'X-Crypt-Iv': self.thisiv,
                    'Accept': '*/*'
                })
            else:
                self.s.headers.update({
                    'X-PERF-SCENE-TIME': '8619',
                    'X-PERF-APP-BUILD-NUMBER': '0',
                    'X-PERF-NETWORK-REQ-LAST': '1',
                    'X-PERF-DISC-FREE': '5395',
                    'X-PERF-FPS-LAST-MED': '59.99',
                    'X-APP-VERSION': self.version,
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
                    'X-Crypt-Iv': self.thisiv,
                    'X-PERF-MEM-AVAILABLE': '24',
                    'X-OS-TYPE': self.device,
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
            if self.region == 2:
                self.s.headers.update({
                    'X-Unity-Version': '2018.4.3f1',
                    'X-Crypt-Iv': self.thisiv,
                    'Accept-Language': 'en-us',
                    'X_CHANNEL': '1',
                    'Content-Type': 'application/x-haut-hoiski',
                    'User-Agent': 'en/17 CFNetwork/1206 Darwin/20.1.0',
                    'X-OS-TYPE': '1',
                    'X-APP-VERSION': self.version
                })
            else:
                self.s.headers.update({
                    'X-Unity-Version': '2018.4.20f1',
                    'X-Crypt-Iv': self.thisiv,
                    'Accept-Language': 'en-us',
                    'Content-Type': 'application/x-haut-hoiski',
                    'User-Agent':
                    'forwardworks/194 CFNetwork/1206 Darwin/20.1.0',
                    'X-OS-TYPE': self.device,
                    'X-APP-VERSION': self.version
                })
        elif i == 2:
            self.s.headers.update({
                'X-Unity-Version': '2018.4.20f1',
                'X-Crypt-Iv': self.thisiv,
                'Accept-Language': 'en-us',
                'Content-Type': 'application/x-haut-hoiski',
                'User-Agent': 'iPad6Gen/iOS 14.2',
                'X-OS-TYPE': self.device,
                'X-APP-VERSION': self.version,
                'X-SESSION': self.session_id
            })
        else:
            self.s.headers.update({
                'X-Unity-Version': '2018.4.20f1',
                'X-Crypt-Iv': self.thisiv,
                'Accept-Language': 'en-us',
                'Content-Type': 'application/x-haut-hoiski',
                'User-Agent': 'forwardworks/194 CFNetwork/1206 Darwin/20.1.0',
                'X-OS-TYPE': self.device,
                'X-APP-VERSION': self.version
            })

    def rndid(self):
        return self.c.rndid()

    def login(self):
        if self.region == 1 or hasattr(self, 'isReroll'):
            data = self.callAPI('login', {
                "password": self.password,
                "uuid": self.uuid
            })
        else:
            data = self.callAPI(
                'sdk/login', {
                    "platform": self.platform,
                    "sess": self.sess,
                    "sdk": "BC4D6C8AE94230CC",
                    "region": "non_mainland",
                    "uin": self.uin
                })
        return data

    def version_check(self):
        data = self.callAPI('version_check', None)
        return data

    def signup(self):
        data = self.callAPI('signup', '')
        return data

    def rpc(self, method, prms):
        return self.callAPI(
            'rpc', {
                "rpc": {
                    "jsonrpc": "2.0",
                    "id": self.rndid(),
                    "prms": json.dumps(prms, separators=(',', ':')),
                    "method": method
                }
            })

    def player_add(self):
        data = self.rpc('player/add', {})
        return data

    def app_constants(self):
        data = self.rpc('app/constants', {})
        return data

    def player_tutorial(self,
                        charaIdList=None,
                        step=None,
                        charaRarityList=None,
                        name=None,
                        gacha_fix=None):
        if charaIdList is None:
            data = self.rpc('player/tutorial', {})
        else:
            data = self.rpc(
                'player/tutorial', {
                    "charaIdList": charaIdList,
                    "step": step,
                    "charaRarityList": charaRarityList,
                    "name": name,
                    "gacha_fix": gacha_fix
                })
        return data

    def player_update_device_token(self, device_token):
        data = self.rpc(
            'player/update_device_token', {
                "device_token":
                "{length=32,bytes=0x034e8400c0f9937e142a2d2388845780...ef6bb16672be3d4a}"
            })
        return data

    def system_version_manage(self):
        data = self.rpc('system/version_manage', {})
        return data

    def player_sync(self):
        data = self.rpc('player/sync', {})
        return data

    def player_tutorial_gacha_single(self):
        data = self.rpc('player/tutorial_gacha_single', {})
        return data

    def adjust_add(self, event_id):
        data = self.rpc('adjust/add', {"event_id": event_id})
        return data

    def player_tutorial_choice_characters(self):
        data = self.rpc('player/tutorial_choice_characters', {})
        return data

    def player_characters(self, updated_at, page):
        data = self.rpc('player/characters', {
            "updated_at": updated_at,
            "page": page
        })
        return data

    def player_weapons(self, updated_at=0, page=1):
        if not hasattr(self, 'equipments'):
            self.weapons = []
        data = self.rpc('player/weapons', {
            "updated_at": updated_at,
            "page": page
        })
        if len(data['result']['_items']) <= 0: return data
        self.weapons = self.weapons + data['result']['_items']
        return self.player_weapons(updated_at, page + 1)

    def player_weapon_effects(self, updated_at, page):
        data = self.rpc('player/weapon_effects', {
            "updated_at": updated_at,
            "page": page
        })
        return data

    def player_equipments(self, updated_at=0, page=1):
        if not hasattr(self, 'equipments'):
            self.equipments = []
        data = self.rpc('player/equipments', {
            "updated_at": updated_at,
            "page": page
        })
        if len(data['result']['_items']) <= 0: return data
        self.equipments = self.equipments + data['result']['_items']
        return self.player_equipments(updated_at, page + 1)

    def player_equipment_effects(self, updated_at, page):
        data = self.rpc('player/equipment_effects', {
            "updated_at": updated_at,
            "page": page
        })
        return data

    def player_innocents(self, updated_at, page):
        data = self.rpc('player/innocents', {
            "updated_at": updated_at,
            "page": page
        })
        return data

    def player_clear_stages(self, updated_at, page):
        data = self.rpc('player/clear_stages', {
            "updated_at": updated_at,
            "page": page
        })
        return data

    def player_index(self):
        data = self.rpc('player/index', {})
        return data

    def player_agendas(self):
        data = self.rpc('player/agendas', {})
        return data

    def player_boosts(self):
        data = self.rpc('player/boosts', {})
        return data

    def player_character_collections(self):
        data = self.rpc('player/character_collections', {})
        return data

    def player_decks(self):
        data = self.rpc('player/decks', {})
        self.deck = [
            data['result']['_items'][self.activeParty -
                                     1]['t_character_ids'][x]
            for x in data['result']['_items'][self.activeParty -
                                              1]['t_character_ids']
        ]
        return data

    def friend_index(self):
        data = self.rpc('friend/index', {})
        return data

    def friend_send_sardines(self):
        data = self.rpc('friend/send_act', {"target_t_player_id":0})
        if (data['error'] == 'You cannot send more sardine.'):
            return data['error']
        print(f"Sent sardines to {data['result']['send_count_total']} friends")
        return data

    def trophy_get_reward_daily(self, receive_all=1, id=0):
        data = self.rpc('trophy/get_reward_daily', {
            "receive_all": receive_all,
            "id": id
        })
        return data

    def trophy_get_reward(self, receive_all=1, id=0):
        data = self.rpc('trophy/get_reward', {
            "receive_all": receive_all,
            "id": id
        })
        return data

    def trophy_get_reward_repetition(self, receive_all=1, id=0):
        with suppress(Exception):
            data = self.rpc('trophy/get_reward_repetition', {
                "receive_all": receive_all,
                "id": id
            })
            return data

    def player_home_customizes(self):
        data = self.rpc('player/home_customizes', {})
        return data

    def player_items(self):
        data = self.rpc('player/items', {})
        self.items = data['result']['_items']
        return data

    def passport_index(self):
        data = self.rpc('passport/index', {})
        return data

    def player_stone_sum(self):
        data = self.rpc('player/stone_sum', {})
        self.log('free stones:%s paid stones:%s' %
                 (data['result']['_items'][0]['num'],
                  data['result']['_items'][1]['num']))
        self.gems = data['result']['_items'][0]['num']
        return data

    def player_sub_tutorials(self):
        data = self.rpc('player/sub_tutorials', {})
        return data

    def player_gates(self):
        data = self.rpc('player/gates', {})
        return data

    def event_index(self):
        data = self.rpc('event/index', {})
        return data

    def event_index_eventid(self, eventids):
        data = self.rpc('event/index', {"m_event_ids": eventids})
        return data

    def stage_boost_index(self):
        data = self.rpc('stage_boost/index', {})
        return data

    def information_popup(self):
        data = self.rpc('information/popup', {})
        return data

    def player_character_mana_potions(self):
        data = self.rpc('player/character_mana_potions', {})
        return data

    def potential_current(self):
        data = self.rpc('potential/current', {})
        return data

    def potential_conditions(self):
        data = self.rpc('potential/conditions', {})
        return data

    def character_boosts(self):
        data = self.rpc('character/boosts', {})
        return data

    def survey_index(self):
        data = self.rpc('survey/index', {})
        return data

    def survey_start(self, m_survey_id, hour, t_character_ids, auto_rebirth_t_character_ids=[]):
        data = self.rpc('survey/start',{"m_survey_id":m_survey_id,"hour":hour,"t_character_ids":t_character_ids,"auto_rebirth_t_character_ids":auto_rebirth_t_character_ids})
        return data

    def survey_end(self, m_survey_id, cancel):
        data = self.rpc('survey/end', {"m_survey_id":m_survey_id,"cancel":cancel})
        return data

    # bribe data [{"m_item_id":401,"num":4}]
    def survey_use_bribe_item(self, m_survey_id, bribe_data):
        data = self.rpc('survey/use_bribe_item', {"m_survey_id":m_survey_id,"bribe_data":bribe_data})
        return data

    def kingdom_entries(self):
        data = self.rpc('kingdom/entries', {})
        return data

    def update_admin_flg(self):
        data = self.rpc('debug/update_admin_flg', {})
        return data

    def breeding_center_list(self):
        data = self.rpc('breeding_center/list', {})
        return data

    def trophy_daily_requests(self):
        data = self.rpc('trophy/daily_requests', {})
        return data

    def weapon_equipment_update_effect_unconfirmed(self):
        data = self.rpc('weapon_equipment/update_effect_unconfirmed', {})
        return data

    def trophy_character_missions(self, m_character_ids, updated_at):
        data = self.rpc('trophy/character_missions', {
            "m_character_ids": m_character_ids,
            "updated_at": updated_at
        })
        return data

    def system_version_update(self):
        data = self.rpc(
            'system/version_update', {
                "app_version": self.version,
                "resouce_version": self.newest_resource_version,
                "database_version": "0"
            })
        return data

    def login_update(self):
        data = self.rpc('login/update', {})
        return data

    def player_badge_homes(self):
        data = self.rpc('player/badge_homes', {})
        return data

    def trophy_beginner_missions(self, sheet_type=None):
        data = self.rpc(
            'trophy/beginner_missions',
            {} if sheet_type is None else {'sheet_type': sheet_type})
        return data

    def present_index(self, is_limit_notice=None, conditions=None, order=None):
        if is_limit_notice is not None:
            data = self.rpc('present/index',
                            {"is_limit_notice": is_limit_notice})
        else:
            data = self.rpc('present/index', {
                "conditions": conditions,
                "order": order
            })
        return data

    def sub_tutorial_read(self, m_sub_tutorial_id):
        data = self.rpc('sub_tutorial/read',
                        {"m_sub_tutorial_id": m_sub_tutorial_id})
        return data

    def present_history(self):
        data = self.rpc('present/history', {})
        return data

    def present_receive(self, receive_ids, conditions, order):
        data = self.rpc('present/receive', {
            "receive_ids": receive_ids,
            "conditions": conditions,
            "order": order
        })
        return data

    def getmail(self):
        did = set()
        while (1):
            ids = self.present_index(conditions=[0, 1, 2, 3, 4, 99],
                                     order=1)['result']['_items']
            msgs = []
            for i in ids:
                if i['id'] in did: continue
                msgs.append(i['id'])
                did.add(i['id'])
            if len(msgs) >= 1:
                self.present_receive(
                    receive_ids=msgs[0:len(msgs) if len(msgs) <= 20 else 20],
                    conditions=[0, 1, 2, 3, 4, 99],
                    order=1)
            else:
                break

    def gacha_available(self):
        data = self.rpc('gacha/available', {})
        return data

    def gacha_do(self, is_gacha_free, price, item_type, num, m_gacha_id,
                 item_id):
        data = self.rpc(
            'gacha/do', {
                "is_gacha_free": is_gacha_free,
                "price": price,
                "item_type": item_type,
                "num": num,
                "m_gacha_id": m_gacha_id,
                "item_id": item_id
            })
        return data

    def gacha_sums(self):
        data = self.rpc('gacha/sums', {})
        return data

    def getfreegacha(self):
        res = self.gacha_do(is_gacha_free=True,
                      price=0,
                      item_type=2,
                      num=1,
                      m_gacha_id=100001,
                      item_id=0)
        unit_obtained = self.getChar(res['result']['gacha_result'][0]['item_id'])
        print(f"Obtained {res['result']['gacha_result'][0]['rarity']}★ character {unit_obtained['name']}")

    def battle_status(self):
        data = self.rpc('battle/status', {})
        return data

    def player_badges(self):
        data = self.rpc('player/badges', {})
        return data

    def boltrend_exchange_code(self, code):
        data = self.rpc('boltrend/exchange_code', {"code": code})
        return data

    def rndAlp(self, n):
        return ''.join([
            random.choice(string.ascii_lowercase)
            for x in range(random.randint(n - 1, n))
        ])

    def rndUser(self):
        return self.rndAlp(7).title()

    def battle_help_list(self):
        data = self.rpc('battle/help_list', {})
        return data

    def battle_start(self, m_stage_id, help_t_player_id, help_t_character_id,
                     act, help_t_character_lv):
        data = self.rpc(
            'battle/start', {
                "t_character_ids": [],
                "t_deck_no": self.activeParty,
                "m_stage_id": m_stage_id,
                "m_guest_character_id": 0,
                "help_t_player_id": help_t_player_id,
                "t_raid_status_id": 0,
                "help_t_character_id": help_t_character_id,
                "auto_rebirth_t_character_ids": self.reincarnationIDs,
                "act": act,
                "help_t_character_lv": help_t_character_lv
            })
        return data

    def battle_end(self, battle_exp_data, m_stage_id, battle_type,
                   result, command_count, equipment_id=0, equipment_type=0, m_tower_no=0):
        data = self.rpc(
            'battle/end', {
                "battle_exp_data": battle_exp_data,
                "equipment_type": equipment_type,
                "steal_hl_num": random.randint(2364, 4132), # missing
                "m_tower_no": m_tower_no,
                "raid_battle_result": "",
                "m_stage_id": m_stage_id,
                "total_receive_damage": 0, # missing
                "equipment_id": equipment_id,
                "killed_character_num": 0, # missing
                "t_raid_status_id": 0,
                "battle_type": battle_type,
                "result": result,
                "innocent_dead_flg": 0,
                "tower_attack_num": 0, # missing
                "max_once_damage": int(random.uniform(10000, 10000000) * 10), # missing
                "mission_status": "1,1,1", #missing
                "command_count": command_count, # missing
                "prinny_bomb_num": 0, # missing
                #3 star finish
                "common_battle_result":"eyJhbGciOiJIUzI1NiJ9.eyJoZmJtNzg0a2hrMjYzOXBmIjoiMSwxLDEiLCJ5cGIyODJ1dHR6ejc2Mnd4IjoyNTkxNjg1OTc1MjQsImRwcGNiZXc5bXo4Y3V3d24iOjAsInphY3N2NmpldjRpd3pqem0iOjAsImt5cXluaTNubm0zaTJhcWEiOjAsImVjaG02dGh0emNqNHl0eXQiOjAsImVrdXN2YXBncHBpazM1amoiOjAsInhhNWUzMjJtZ2VqNGY0eXEiOjR9.4NWzKTpAs-GrjbFt9M6eEJEbEviUf5xvrYPGiIL4V0k"
              })
        return data

    def item_use(self, use_item_id, use_item_num):
        data = self.rpc('item/use', {
            "use_item_id": use_item_id,
            "use_item_num": use_item_num
        })
        return data

    def getbattle_exp_data(self, start):
        res = []
        for d in start['result']['enemy_list']:
            for r in d:
                res.append({
                    "finish_member_ids": self.deck,
                    "finish_type": random.choice([1, 2, 3]),
                    "m_enemy_id": d[r]
                })
        return res

    def battle_story(self, m_stage_id):
        data = self.rpc('battle/story', {"m_stage_id": m_stage_id})
        return data

    def getStage(self, i):
        i = int(i)
        for s in gamedata['stages']:
            if i == s['id']:
                return s

    def getItem(self, i):
        for s in gamedata['items']:
            if i == s['id']:
                return s

    def getUnit(self, i):
        for s in gamedata['units']:
            if i == s['id']:
                return s

    def getChar(self, i):
        for s in gamedata['characters']:
            if i == s['id']:
                return s

    def getEquip(self, i):
        for s in gamedata['equip']:
            if i == s['id']:
                return s

    def getWeapon(self, i):
        for s in gamedata['weapon']:
            if i == s['id']:
                return s

    def doQuest(self, m_stage_id=101102):
        stage = self.getStage(m_stage_id)
        self.log('doing quest:%s [%s]' % (stage['name'], m_stage_id))
        if stage['exp'] == 0:
            return self.battle_story(m_stage_id)
        help_players = self.battle_help_list()['result']['help_players'][0]
        start = self.battle_start(
            m_stage_id=m_stage_id,
            help_t_player_id=help_players['t_player_id'],
            help_t_character_id=help_players['t_character']['id'],
            act=stage['act'],
            help_t_character_lv=help_players['t_character']['lv'])
        if 'result' not in start:
            return
        self.battle_help_list()
        end = self.battle_end(battle_exp_data=self.getbattle_exp_data(start),
                              m_stage_id=m_stage_id,
                              battle_type=1,
                              result=1,
                              command_count=9)
        res = self.parseReward(end)
        return res

    def doQuest_forcefriend(self, m_stage_id, help_t_player_id, help_t_character_id, help_t_character_lv):
        stage = self.getStage(m_stage_id)
        self.log('doing quest:%s [%s]' % (stage['name'], m_stage_id))
        if stage['exp'] == 0:
            return self.battle_story(m_stage_id)
        start = self.battle_start(
            m_stage_id=m_stage_id,
            help_t_player_id=help_t_player_id,
            help_t_character_id=help_t_character_id,
            act=stage['act'],
            help_t_character_lv=help_t_character_lv)
        if 'result' not in start:
            return
        self.battle_help_list()
        end = self.battle_end(battle_exp_data=self.getbattle_exp_data(start),
                              m_stage_id=m_stage_id,
                              battle_type=1,
                              result=1,
                              command_count=9)
        res = self.parseReward(end)
        return res

    def item_world_start(self, equipment_id, equipment_type=1):
        data = self.rpc(
            'item_world/start', {
                "equipment_type": equipment_type,
                "t_deck_no": self.activeParty,
                "equipment_id": equipment_id,
                "auto_rebirth_t_character_ids": self.reincarnationIDs
            })
        return data

    def getDiffWeapon(self, i):
        try:
            if 'after_t_weapon' not in i[
                    'result'] and 'after_t_equipment' not in i['result']:
                return False
            stuff = self.weapons if 'after_t_weapon' in i[
                'result'] else self.equipments
            i = i['result']['after_t_weapon' if 'after_t_weapon' in
                            i['result'] else 'after_t_equipment']
            res = [str(i['id'])]
            for k, w in enumerate(stuff):
                if w['id'] == i['id']:
                    for j in i:
                        if i[j] != w[j]:
                            s = '%s: %s -> %s' % (j, w[j], i[j])
                            res.append(s)
                    stuff[k] = i
            return ', '.join(res)
        except:
            return ''

    def upgradeItems(self, ensureDrops=False, getOnlyWeapons=False, runLimit=0, raid_farming_party=1):
        count = 0
        limit = runLimit
        self.EnsureDrops = ensureDrops
        self.GetOnlyWeapons = getOnlyWeapons
        self.player_weapons()
        for w in self.weapons:
            if w['lv'] >= w['lv_max']: continue
            itemRank = self.get_item_rank(w)
            #if  itemRank < 40: continue
            #if w['rarity_value'] < 70: continue
            self.trophy_get_reward_repetition()
            count += 1
            if (count > limit and limit > 0):
                return
            while (1):
                if not self.doItemWorld(w['id'], equipment_type=1): break

            self.raid_farm_shared_bosses(raid_farming_party)
        self.player_equipments()
        for e in self.equipments:
            #if e['lv']>=e['lv_max'] or e['m_equipment_id']!= 50010:	continue
            if e['lv'] >= e['lv_max']: continue
            itemRank = self.get_item_rank(e)
            #if itemRank < 40: continue
            #if e['rarity_value'] < 70: continue
            self.trophy_get_reward_repetition()
            count += 1
            if (count > limit and limit > 0):
                return
            while (1):
                if not self.doItemWorld(e['id'], equipment_type=2): break

            self.raid_farm_shared_bosses(raid_farming_party)

    def tower_start(self, m_tower_no):
        data = self.rpc('tower/start', {
            "t_deck_no": self.activeParty,
            "m_tower_no": m_tower_no
        })
        return data

    def doTower(self, m_tower_no=1):
        start = self.tower_start(m_tower_no)
        end = self.battle_end(battle_exp_data=self.getbattle_exp_data(start),
                              m_tower_no=m_tower_no,
                              m_stage_id=0,
                              battle_type=4,
                              result=1,
                              command_count=9)
        return end

    def parseStart(self, start):
        if 'result' in start and 'reward_id' in start['result']:
            reward_id = start['result']['reward_id'][10]
            reward_type = start['result']['reward_type'][10]
            reward_rarity = start['result']['reward_rarity'][10]
        #stage with no drops or ensureDrops is false, continue
        if start['result']['stage'] % 10 != 0 or self.EnsureDrops == False:
            return 1
        #no drop, ensuring drops, retry
        if reward_id == 101:
            return 5
        #drop, no Item General/King/God stage, continue
        if start['result']['stage'] not in set([30, 60, 90, 100]):
            return 1
        # drop, rarity less than minrare, retry
        if reward_rarity < self.minrare:
            return 5
        #equipment drop, but farming only weapons, retry
        if reward_type == 4 and self.GetOnlyWeapons == True:
            return 5
        item = self.getWeapon(reward_id) if reward_type == 3 else self.getEquip(reward_id)
        if item is None:
            item = {'name': ''}
        self.log('[+] found item:%s with rarity:%s' %
                 (item['name'], reward_rarity))
        return 1
        #item king/god stages, farm
        if start['result']['stage'] in set([30, 60, 90, 100]):
            # no common
            if start['result']['reward_rarity'][10] < 40:
                return 5
            # Rares
            if start['result']['reward_rarity'][10] < 70:
                return 5
            # Legendaries
            if start['result']['reward_rarity'][10] >= 70:
                return 1
            #no shield
            # if start['result']['reward_id'][10] == 10035 and start['result']['reward_type'][10] == 4:
            # 	return 0
            #if start['result']['reward_rarity'][10] >= 40 and start['result']['reward_id'][10] != 10035 and start['result']['reward_id'][10] != 40009 or start['result']['reward_rarity'][10] >= 70:
            #if start['result']['reward_rarity'][10] >= 70 and start['result']['reward_id'][10] != 10035 and start['result']['reward_id'][10] != 40009:
            #	return 1
        return 1

    def doItemWorld(self, equipment_id=None, equipment_type=1):
        if equipment_id is None:
            self.log('missing equip')
            return
        start = self.item_world_start(equipment_id,
                                      equipment_type=equipment_type)
        if 'result' not in start: return False
        result = self.parseStart(start)
        end = self.battle_end(battle_exp_data=self.getbattle_exp_data(start),
                              m_stage_id=0,
                              battle_type=5,
                              result=result,
                              command_count=9,
                              equipment_type=equipment_type,
                              equipment_id=equipment_id)
        res = self.getDiffWeapon(end)
        self.log(res)
        return 1

    def getGain(self, t):
        for j in self.items:
            if j['m_item_id'] == t['m_item_id']:
                return t['num'] - j['num']

    def parseReward(self, end):
        try:
            drop_result = end
            rpcid = drop_result['id']
            current_id = drop_result['result']['after_t_stage_current']['current_id']
            drop_result = drop_result['result']['drop_result']
            db = db2.Database()
            for e in drop_result:
                if e == 'after_t_item':
                    for t in drop_result[e]:
                        i = self.getItem(t['m_item_id'])
                        self.log('%s +%s' % (i['name'], self.getGain(t)))
                        db.add(t['m_item_id'], 0, self.getGain(t), current_id,
                               rpcid)
                elif e == 'drop_character':
                    for t in drop_result[e]:
                        self.log(
                            'unit:%s lv:%s rarity:%s*' %
                            (self.getChar(t['m_character_id'])['class_name'],
                             t['lv'], t['rarity']))
                        db.add(t['m_character_id'], 1, 1, current_id, rpcid)
                elif e == 'stones':
                    self.log('+%s nether quartz' %
                             (drop_result[e][0]['num'] - self.gems))
        except:
            print("Error logging item")

    def getDone(self, page=1):
        if not hasattr(self, 'done'):
            self.done = set()
        r = self.player_clear_stages(updated_at=0,page=page)['result']['_items']
        if len(r) <= 0:
            return
        for i in r:
            if i['clear_num'] >= 1:
                self.done.add(i['m_stage_id'])
        return self.getDone(page + 1)

    def item_world_persuasion(self):
        data = self.rpc('item_world/persuasion', {})
        return data

    def completeStory(self, m_area_id=None, limit=None, farmingAll=False):
        if not farmingAll:
            self.getDone()
        ss = []
        for s in gamedata['stages']:
            ss.append(s['id'])
        ss.sort(reverse=False)
        #ss=sorted(ss)
        i = 0
        blacklist = set()
        for s in ss:
            if limit is not None and i >= limit: return False
            #print(s,self.getStage(s)['m_area_id'])
            if m_area_id is not None and m_area_id != self.getStage(s)['m_area_id']:
                continue
            if not farmingAll and s in self.done: continue
            if self.getStage(s)['m_area_id'] in blacklist: continue
            try:
                self.doQuest(s)
            except KeyboardInterrupt:
                return False
            except:
                #print(traceback.format_exc())
                self.log('failed %s %s' % (s, self.getStage(s)['m_area_id']))
                #return False
                blacklist.add(self.getStage(s)['m_area_id'])
                continue
            self.player_stone_sum()
            self.player_items()
            i += 1

    def dologin(self):
        self.login()
        self.player_index()
        self.player_tutorial()
        #self.getmail()
        #self.getmail()
        self.player_stone_sum()
        self.app_constants()
        self.player_tutorial()
        self.battle_status()
        self.player_characters(updated_at=0, page=1)
        self.player_weapons(updated_at=0, page=1)
        self.player_equipments(updated_at=0, page=1)
        self.player_innocents(updated_at=0, page=1)
        self.player_index()
        self.player_agendas()
        self.player_boosts()
        self.player_character_collections()
        self.player_decks()
        self.friend_index()
        self.player_home_customizes()
        self.player_items()
        self.passport_index()
        self.player_stone_sum()
        self.player_sub_tutorials()
        self.system_version_manage()
        self.player_gates()
        self.event_index()
        self.stage_boost_index()
        self.information_popup()
        self.player_character_mana_potions()
        self.player_equipments(updated_at=0, page=2)
        self.player_innocents(updated_at=0, page=2)
        self.player_badges()
        self.system_version_manage()
        self.player_update_device_token(device_token='')
        self.login_update()
        self.player_badge_homes()
        self.trophy_beginner_missions()
        #self.getmail()
        #self.getmail()
        #self.getfreegacha()
        self.db.addAccount(self.sess, '', self.uin, self.gems)
        self.updateAccount()

    def updateAccount(self):
        if hasattr(self, 'sess'):
            self.db.updateAccount(int(self.uin), self.gems, self.sess)

    def shop_equipment_items(self):
        data = self.rpc('shop/equipment_items', {})
        return data
    
    def shop_index(self):
        data = self.rpc('shop/index', {})
        return data

    def shop_gacha(self):
        data = self.rpc('shop/garapon', {"m_garapon_id":1})
        return data

    def shop_equipment_shop(self):
        data = self.rpc('shop/equipment_shop', {})
        return data

    def shop_buy_equipment(self, item_type, itemids):
        data = self.rpc('shop/buy_equipment', {
            "item_type": item_type,
            "ids": itemids
        })
        return data

    def shop_change_equipment_items(self, shop_rank=32):
        updateNumber = self.shop_equipment_shop()['result']['lineup_update_num']
        if (updateNumber < 5):
            data = self.rpc('shop/change_equipment_items', {"shop_rank": shop_rank})
        else:
            self.log('Free refreshes used up already')
            data = 0
        return data

    def shop_buy_item(self, itemid, quantity):
        data = self.rpc('shop/buy_item', {"id": itemid, "quantity": quantity})
        return data

    def getAllInnocents(self):
        fullInnocents = []
        currPage = 0
        while True:
            currPage = currPage + 1
            data = self.player_innocents(updated_at=0, page=currPage)
            innocents = data['result']['_items']
            if len(innocents) >= 1:
                new_innocents = [*fullInnocents, *innocents]
                fullInnocents = new_innocents
            else:
                break
        return fullInnocents

    def initInnocentPerEquipment(self, minimumEffectRank=7):
        self.log('retrieving full list of innocents...')
        innocents = self.getAllInnocents()
        equipmentsInnocents = {}
        if len(innocents) >= 1:
            self.log('generating equip-id => innocent hasmapmap...')
            for innocent in innocents:
                equipmentId = innocent['place_id']
                if equipmentId in equipmentsInnocents:
                    equipmentsInnocents[equipmentId]['innocentsArray'][innocent['place_no']] = innocent
                    # equipmentsInnocents[equipmentId][innocent['place_no']]=innocent # if we want an hasmap too...
                else:
                    equipmentsInnocents[equipmentId] = {}
                    equipmentsInnocents[equipmentId]['innocentsArray'] = [None] * 10
                    equipmentsInnocents[equipmentId]['innocentsArray'][innocent['place_no']] = innocent
                    # equipmentsInnocents[equipmentId][innocent['place_no']]=innocent # if we want an hasmap too...
                    equipmentsInnocents[equipmentId]['canSell'] = innocent['effect_rank'] < minimumEffectRank
                if innocent['effect_rank'] >= minimumEffectRank:
                    equipmentsInnocents[equipmentId]['canSell'] = False
            self.log('hashmap generated!')
        return equipmentsInnocents

    def innocent_safe_sellItems(self, minimumEffectRank=5, minimumItemRank=32):
        self.player_equipments()
        self.player_weapons()
        equipments = self.initInnocentPerEquipment(minimumEffectRank)
        selling = []
        for w in self.weapons:
            wId = w['id']
            if self.get_item_rank(w) > minimumItemRank: continue
            #if w['rarity_value']>=minrarity:    continue
            if w['set_chara_id'] != 0: continue
            if w['lv'] > 1: continue
            if w['lock_flg'] == True: continue
            if wId in equipments and equipments[wId]['canSell'] == False:
                continue
            selling.append({'eqtype': 1, 'eqid': wId})
        for e in self.equipments:
            if self.get_item_rank(e) > minimumItemRank: continue
            eId = e['id']
            #if e['rarity_value'] >= minrarity: continue
            if e['set_chara_id'] != 0: continue
            if e['lv'] > 1: continue
            if e['lock_flg'] == True: continue
            if eId in equipments and equipments[eId]['canSell'] == False:
                continue
            selling.append({'eqtype': 2, 'eqid': eId})
        self.log(selling)
        self.log(len(selling))
        if len(selling) >= 1:
            self.log('selling...')
            self.shop_sell_equipment(selling)

    def BuyDailyItemsFromShop(self):
        productData = self.shop_index()['result']['shop_buy_products']['_items']
        print("Buying daily AP Pots and bribe items...")
        #50% AP Pot
        item = [x for x in productData if x['m_product_id'] == 102][0]
        if(item['buy_num'] == 0):
            self.shop_buy_item(102, 2)
        #Golden candy
        item = [x for x in productData if x['m_product_id'] == 107][0]
        if(item['buy_num'] == 0):
            self.shop_buy_item(107, 3)
        #Golden Bar
        item = [x for x in productData if x['m_product_id'] == 108][0]
        if(item['buy_num'] == 0):
            self.shop_buy_item(108, 2)
        #Skip ticket
        item = [x for x in productData if x['m_product_id'] == 1121][0]
        if(item['buy_num'] == 0):
            self.shop_buy_item(1121, 1)

    def BuyAllEquipmentWithInnocents(self):
        equipment_items = self.shop_equipment_items()['result']['_items']
        for i in equipment_items:
            if i['sold_flg']: continue
            if i['innocent_num'] > 0:
                itemIDs = []
                itemIDs.append(i['id']) 
                res = self.shop_buy_equipment(item_type=i['item_type'], itemids=itemIDs)
                if (res['error'] == 'Maximum weapon slot reached' or res['error'] == 'Maximum armour slot reached'):
                    refresh_shop = False

    def shop_sell_equipment(self, sell_equipments):
        data = self.rpc('shop/sell_equipment',
                        {"sell_equipments": sell_equipments})
        return data

    def hospital_index(self):
        data = self.rpc('hospital/index', {})
        return data

    def hospital_roulette(self):
        data = self.rpc('hospital/roulette', {})
        if (data['error'] == 'Not the time to recover'):
            return data['error']
        print(f"Hospital Roulettte - Recovered {data['result']['recovery_num']} AP")
        return data

    def get_item_rank(self, e):
        item_rank = 140
        if 'm_weapon_id' in e:
            weapon = self.getWeapon(e['m_weapon_id'])
            if weapon is not None:
                item_rank = weapon['item_rank']
        elif 'm_equipment_id' in e:
            equip = self.getEquip(e['m_equipment_id'])
            if equip is not None:
                item_rank = equip['item_rank']
        elif 'item_rank' in e:
            item_rank = e['item_rank']
        else:
            raise Exception('unable to determine item rank')
        if item_rank > 100:
            item_rank = item_rank - 100
        return item_rank

    def find_character_by_id(self, unitID):
        iterateNextPage = True
        pageIndex = 1
        m_character_id = 0
        while iterateNextPage:
            charactersInPage = self.player_characters(updated_at=0, page=pageIndex)['result']['_items']
            for i in charactersInPage:
                if i['id'] == unitID:
                    m_character_id = i['m_character_id']
                    break    
            pageIndex+=1
            iterateNextPage = m_character_id == 0 and len(charactersInPage) == 100
        
        allCollections = self.player_character_collections()['result']['_items']
        character = next((x for x in allCollections if x['m_character_id'] == m_character_id), None)
        return character

    def decrypt(self, content, iv):
        res = self.c.decrypt(content,iv)
        if 'fuji_key' in res:
            if sys.version_info >= (3, 0):
                self.c.key = bytes(res['fuji_key'], encoding='utf8')
            else:
                self.c.key = bytes(res['fuji_key'])
            self.session_id = res['session_id']
            self.log('found fuji_key:%s' % (self.c.key))    
    
        
    def bingo_index(self, bingo_id=Constants.Current_Bingo_ID):
        data = self.rpc('bingo/index', {"id":bingo_id})
        return data

    def bingo_lottery(self, bingo_id=Constants.Current_Bingo_ID, use_stone=False):
        data = self.rpc('bingo/lottery', {"id":bingo_id,"use_stone":use_stone})
        return data

    #ids takes an array [57]
    def bingo_receive_reward(self, reward_id):
        data = self.rpc('bingo/receive', {"ids":reward_id})
        return data

if __name__ == "__main__":
    a = API()
    if False:
        a.password = '26eYVYpYVdbwpPkq'
        a.uuid = 'e08ed5d9-61a6-4055-a18e-9795d8f40f47'
        a.dologin()
    else:
        a.reroll()
