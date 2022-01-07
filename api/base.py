# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import requests
import base64
import time
import json
import sys
from data import data as gamedata
from codedbots import codedbots
from boltrend import boltrend

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

head = {'version_check': 0, 'signup': 1, 'login': 1, 'rpc': 2}


class Base(object, metaclass=ABCMeta):
    def __init__(self):
        self.t_deck_no = 0
        self.platform = None
        self.waitn = None
        self.minrare = None
        self.pid = None
        self.session_id = None
        self.newest_resource_version = None
        self.thisiv = None
        self.sdk = None
        self.uuid = None
        self.password = None
        self.device = None
        self.region = None
        self.version = None
        self.mainurl = None
        self.sess = None
        self.uin = None
        self.c = codedbots()
        self.b = boltrend()
        self.s = requests.Session()
        self.s.verify = False
        self.setRegion(1)
        # self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'http://127.0.0.1:8888',})
        self.setDevice(1)

    def setProxy(self, proxy):
        proxy = 'http://' + proxy
        proxy = {'http': proxy, 'https': proxy, }
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

    def setTeamNum(self, r):
        self.t_deck_no = r - 1
        self.player_decks()

    def teamNum(self):
        return self.t_deck_no + 1

    def wait(self, n):
        self.waitn = int(n)

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
            print('[%s] %s' % (time.strftime('%H:%M:%S'), msg))  # .encode('utf-8').encode('ascii', 'ignore')))
        else:
            print('[%s] %s' % (time.strftime('%H:%M:%S'), msg.encode('utf-8')))

    def callAPI(self, url, data=None):
        # if hasattr(self,'waitn') and self.waitn>=1:
        #	time.sleep(self.waitn)
        self.thisiv = self.c.randomiv()
        self.setheaders(url)
        if data is None:
            r = self.s.get(self.mainurl + url)
        else:
            if data != '':
                cdata = self.c.encrypt(data, self.thisiv)
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
                rr = self.item_use(use_item_id=301, use_item_num=1)
                if 'api_error' in rr and rr['api_error']['code'] == 12009:
                    return None
                return self.callAPI(url, data)
            else:
                self.log('server returned error: %s' % (res['api_error']['message']))
        # exit(1)
        if 'password' in res:
            self.password = res['password']
            self.uuid = res['uuid']
            self.log('found password:%s uuid:%s' % (self.password, self.uuid))
        if 'result' in res and 'newest_resource_version' in res['result']:
            self.newest_resource_version = res['result']['newest_resource_version']
            self.log('found resouce:%s' % self.newest_resource_version)
        if 'fuji_key' in res:
            if sys.version_info >= (3, 0):
                self.c.key = bytes(res['fuji_key'], encoding='utf8')
            else:
                self.c.key = bytes(res['fuji_key'])
            self.session_id = res['session_id']
            self.log('found fuji_key:%s' % self.c.key)
        if 'result' in res and 't_player_id' in res['result']:
            if 'player_rank' in res['result']:
                self.log('t_player_id:%s player_rank:%s' % (res['result']['t_player_id'], res['result']['player_rank']))
            self.pid = res['result']['t_player_id']
        if 'result' in res and 'after_t_status' in res['result']:
            self.log('%s / %s rank:%s' % (
                res['result']['after_t_status']['act'], res['result']['after_t_status']['act_max'],
                res['result']['after_t_status']['rank']))
        if 'result' in res and 't_innocent_id' in res['result']:
            if res['result']['t_innocent_id'] != 0:
                self.log('t_innocent_id:%s' % (res['result']['t_innocent_id']))
                status = 0
                while status == 0:
                    status = self.item_world_persuasion()
                    self.log('status:%s' % status)
                    status = status['result']['after_t_innocent']['status']
        return res

    def item_world_persuasion(self):
        data = self.rpc('item_world/persuasion', {})
        return data

    def item_use(self, use_item_id, use_item_num):
        data = self.rpc('item/use', {"use_item_id": use_item_id, "use_item_num": use_item_num})
        return data

    def setheaders(self, i):
        try:
            i = head[i]
        except:
            i = None
        self.s.headers.clear()
        if i == 0:
            if self.region == 2:
                self.s.headers.update({'X-Unity-Version': '2018.4.3f1', 'Accept-Language': 'en-us', 'X_CHANNEL': '1',
                                       'Content-Type': 'application/x-haut-hoiski',
                                       'User-Agent': 'en/17 CFNetwork/1206 Darwin/20.1.0', 'X-OS-TYPE': '1',
                                       'X-APP-VERSION': self.version, 'X-Crypt-Iv': self.thisiv, 'Accept': '*/*'})
            else:
                self.s.headers.update(
                    {'X-PERF-SCENE-TIME': '8619', 'X-PERF-APP-BUILD-NUMBER': '0', 'X-PERF-NETWORK-REQ-LAST': '1',
                     'X-PERF-DISC-FREE': '5395', 'X-PERF-FPS-LAST-MED': '59.99', 'X-APP-VERSION': self.version,
                     'X-PERF-OS-VERSION': 'iOS 14.2', 'X-PERF-CPU-SYS': '0', 'X-PERF-CPU-USER': '40.79',
                     'X-PERF-BUTTERY': '100',
                     'X-PERF-SCENE-TRACE': 'startup_scene,title_scene,startup_scene,title_scene',
                     'X-PERF-NETWORK-ERR-LAST': '0', 'X-PERF-NETWORK-REQ-TOTAL': '1', 'X-PERF-CPU-IDLE': '59.21',
                     'X-PERF-APP-VERSION': '2.11.2', 'X-PERF-FPS-LAST-AVG': '59.23',
                     'User-Agent': 'forwardworks/194 CFNetwork/1206 Darwin/20.1.0', 'X-PERF-MEM-USER': '1624',
                     'X-PERF-LAUNCH-TIME': '20210408T15:50:36Z', 'X-PERF-SCENE': 'title_scene', 'X-PERF-FPS': '59.99',
                     'X-Crypt-Iv': self.thisiv, 'X-PERF-MEM-AVAILABLE': '24', 'X-OS-TYPE': self.device,
                     'X-PERF-LAST-DELTA-TIMES': '16,17,16,17,21,13,16,17,17,17', 'X-PERF-NETWORK-ERR-TOTAL': '0',
                     'X-PERF-DEVICE': 'iPad7,5', 'Content-Type': 'application/x-haut-hoiski', 'X-PERF-OS': 'iOS 14.2',
                     'X-PERF-MEM-PYSIC': '1981', 'X-Unity-Version': '2018.4.20f1', 'X-PERF-TIME': '20210408T15:52:43Z',
                     'X-PERF-APP-ID': 'com.disgaearpg.forwardworks', 'X-PERF-LAUNCH-DURATION': '70363'})
        elif i == 1:
            if self.region == 2:
                self.s.headers.update(
                    {'X-Unity-Version': '2018.4.3f1', 'X-Crypt-Iv': self.thisiv, 'Accept-Language': 'en-us',
                     'X_CHANNEL': '1', 'Content-Type': 'application/x-haut-hoiski',
                     'User-Agent': 'en/17 CFNetwork/1206 Darwin/20.1.0', 'X-OS-TYPE': '1',
                     'X-APP-VERSION': self.version})
            else:
                self.s.headers.update(
                    {'X-Unity-Version': '2018.4.20f1', 'X-Crypt-Iv': self.thisiv, 'Accept-Language': 'en-us',
                     'Content-Type': 'application/x-haut-hoiski',
                     'User-Agent': 'forwardworks/194 CFNetwork/1206 Darwin/20.1.0', 'X-OS-TYPE': self.device,
                     'X-APP-VERSION': self.version})
        elif i == 2:
            self.s.headers.update(
                {'X-Unity-Version': '2018.4.20f1', 'X-Crypt-Iv': self.thisiv, 'Accept-Language': 'en-us',
                 'Content-Type': 'application/x-haut-hoiski', 'User-Agent': 'iPad6Gen/iOS 14.2',
                 'X-OS-TYPE': self.device, 'X-APP-VERSION': self.version, 'X-SESSION': self.session_id})
        else:
            self.s.headers.update(
                {'X-Unity-Version': '2018.4.20f1', 'X-Crypt-Iv': self.thisiv, 'Accept-Language': 'en-us',
                 'Content-Type': 'application/x-haut-hoiski',
                 'User-Agent': 'forwardworks/194 CFNetwork/1206 Darwin/20.1.0', 'X-OS-TYPE': self.device,
                 'X-APP-VERSION': self.version})

    def rndid(self):
        return self.c.rndid()

    def login(self):
        if self.region == 1 or hasattr(self, 'isReroll'):
            data = self.callAPI('login', {"password": self.password, "uuid": self.uuid})
        else:
            data = self.callAPI('sdk/login', {"platform": self.platform, "sess": self.sess, "sdk": "BC4D6C8AE94230CC",
                                              "region": "non_mainland", "uin": self.uin})
        return data

    def version_check(self):
        data = self.callAPI('version_check', None)
        return data

    def signup(self):
        data = self.callAPI('signup', '')
        return data

    def rpc(self, method, prms):
        return self.callAPI('rpc', {
            "rpc": {"jsonrpc": "2.0", "id": self.rndid(), "prms": json.dumps(prms, separators=(',', ':')),
                    "method": method}})

    def app_constants(self):
        data = self.rpc('app/constants', {})
        return data

    def system_version_manage(self):
        data = self.rpc('system/version_manage', {})
        return data

    def login_update(self):
        data = self.rpc('login/update', {})
        return data

    def getmail(self):
        did = set()
        while (1):
            ids = self.present_index(conditions=[0, 1, 2, 3, 4, 99], order=1)['result']['_items']
            msgs = []
            for i in ids:
                if i['id'] in did:    continue
                msgs.append(i['id'])
                did.add(i['id'])
            if len(msgs) >= 1:
                self.present_receive(receive_ids=msgs[0:len(msgs) if len(msgs) <= 20 else 20],
                                     conditions=[0, 1, 2, 3, 4, 99], order=1)
            else:
                break

    def present_receive(self, receive_ids, conditions, order):
        data = self.rpc('present/receive', {"receive_ids": receive_ids, "conditions": conditions, "order": order})
        return data

    def present_index(self, is_limit_notice=None, conditions=None, order=None):
        if is_limit_notice is not None:
            data = self.rpc('present/index', {"is_limit_notice": is_limit_notice})
        else:
            data = self.rpc('present/index', {"conditions": conditions, "order": order})
        return data

    def adjust_add(self, event_id):
        data = self.rpc('adjust/add', {"event_id": event_id})
        return data

    def friend_index(self):
        data = self.rpc('friend/index', {})
        return data

    def friend_send_act(self, target_t_player_id=0):
        data = self.rpc('friend/send_act', {"target_t_player_id": target_t_player_id})
        return data

    def friend_receive_act(self, target_t_player_id=0):
        data = self.rpc('friend/receive_act', {"target_t_player_id": target_t_player_id})
        return data

    def trophy_get_reward_daily(self, receive_all=1, id=0):
        data = self.rpc('trophy/get_reward_daily', {"receive_all": receive_all, "id": id})
        return data

    def trophy_get_reward(self, receive_all=1, id=0):
        data = self.rpc('trophy/get_reward', {"receive_all": receive_all, "id": id})
        return data

    def trophy_get_reward_repetition(self, receive_all=1, id=0):
        data = self.rpc('trophy/get_reward_repetition', {"receive_all": receive_all, "id": id})
        return data

    def event_index(self):
        data = self.rpc('event/index', {})
        return data

    def stage_boost_index(self):
        data = self.rpc('stage_boost/index', {})
        return data

    def information_popup(self):
        data = self.rpc('information/popup', {})
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
        data = self.rpc('trophy/character_missions', {"m_character_ids": m_character_ids, "updated_at": updated_at})
        return data

    def system_version_update(self):
        data = self.rpc('system/version_update',
                        {"app_version": self.version, "resouce_version": self.newest_resource_version,
                         "database_version": "0"})
        return data

    @abstractmethod
    def player_decks(self):
        pass

    def stages(self):
        return gamedata['stages']

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
            if 'm_character_id' not in s:
                continue
            if i == s['m_character_id']:
                return s
        return {'class_name': 'MISSING'}

    def getEquip(self, i):
        for s in gamedata['equip']:
            if i == s['id']:
                return s

    def getWeapon(self, i):
        for s in gamedata['weapon']:
            if i == s['id']:
                return s

    def get_item_rank(self, e):
        if 'm_weapon_id' in e:
            item_rank = self.getWeapon(e['m_weapon_id'])['item_rank']
        elif 'm_equipment_id' in e:
            item_rank = self.getEquip(e['m_equipment_id'])['item_rank']
        elif 'item_rank' in e:
            item_rank = e['item_rank']
        else:
            raise Exception('unable to determine item rank')

        assert isinstance(item_rank, int)

        if item_rank > 100:
            item_rank = item_rank - 100
        return item_rank
