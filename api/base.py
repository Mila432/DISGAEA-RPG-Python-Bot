# -*- coding: utf-8 -*-
from abc import ABCMeta

from api.client import Client
from api.game_data import GameData
from api.logger import Logger
from api.options import Options
from api.player_data import PlayerData


class Base(object, metaclass=ABCMeta):
    def __init__(self):
        self.gd: GameData = GameData()
        self.o: Options = Options(region=1, device=1)
        self.pd: PlayerData = PlayerData(options=self.o)
        self.client: Client = Client(self.o)
        self.logger: Logger = Logger()

    @property
    def current_ap(self):
        return self.o.current_ap

    @property
    def options(self):
        return self.o

    def log(self, msg):
        Logger.info(msg)

    def log_err(self, msg):
        Logger.error(msg)

    def get_weapon_diff(self, i):
        if not i or 'result' not in i or (
                'after_t_weapon' not in i['result'] and 'after_t_equipment' not in i['result']):
            return False
        stuff = self.pd.weapons if 'after_t_weapon' in i['result'] else self.pd.equipment
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

    def check_resp(self, resp):
        if 'api_error' in resp:
            raise resp['api_error']['message']
