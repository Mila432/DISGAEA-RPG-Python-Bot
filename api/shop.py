from abc import ABCMeta

from api.player import Player


class Shop(Player, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    def shop_equipment_items(self):
        data = self.rpc('shop/equipment_items', {})
        return data

    def shop_equipment_shop(self):
        data = self.rpc('shop/equipment_shop', {})
        return data

    def shop_buy_equipment(self, item_type, itemid):
        data = self.rpc('shop/buy_equipment', {"item_type": item_type, "id": itemid})
        return data

    def shop_change_equipment_items(self, shop_rank=1):
        data = self.rpc('shop/change_equipment_items', {"shop_rank": shop_rank})
        return data

    def buyAll(self, minrarity=None):
        items = self.shop_equipment_items()['result']['_items']
        for i in items:
            if i['sold_flg']:    continue
            if minrarity is not None and i['rarity'] < minrarity:    continue
            self.log('found item:%s rare:%s' % (i['id'], i['rarity']))
            self.shop_buy_equipment(item_type=i['item_type'], itemid=i['id'])

    def shop_buy_item(self, itemid, quantity):
        data = self.rpc('shop/buy_item', {"id": itemid, "quantity": quantity})
        return data

    def shop_sell_equipment(self, sell_equipments):
        data = self.rpc('shop/sell_equipment', {"sell_equipments": sell_equipments})
        return data

    # max_innocent_rank (effect_rank)
    #   ancient = 11+
    #   legendary = 9-10
    #   rare = 5-8
    #   common = 1-4
    def sellItems(self, max_rarity=40, max_rank=100, keep_max_lvl=False, only_max_lvl=False, max_innocent_rank=10):
        self.player_equipments()
        self.player_weapons()
        selling = []
        for w in self.weapons:
            if not self.can_sell_item(w, max_rarity, max_rank, keep_max_lvl, only_max_lvl, max_innocent_rank):
                continue
            self.log_sell(w)
            selling.append({'eqtype': 1, 'eqid': w['id']})
        for w in self.equipments:
            if not self.can_sell_item(w, max_rarity, max_rank, keep_max_lvl, only_max_lvl, max_innocent_rank):
                continue
            self.log_sell(w)
            selling.append({'eqtype': 2, 'eqid': w['id']})
        if len(selling) >= 1:
            self.shop_sell_equipment(selling)

    def log_sell(self, w):
        item = self.getWeapon(w['m_weapon_id']) if 'm_weapon_id' in w else self.getEquip(w['m_equipment_id'])
        self.log(
            '[-] sell item: "%s" rarity: %s rank: %s lv: %s lv_max: %s locked: %s' %
            (item['name'], w['rarity_value'], self.get_item_rank(w), w['lv'],
             w['lv_max'], w['lock_flg'])
        )

    def can_sell_item(self, w, max_rarity=39, max_rank=99, keep_max_lvl=False, only_max_lvl=False, max_innocent_rank=8,
                      max_innocent_type=7):
        if keep_max_lvl and w['lv'] == w['lv_max']:
            self.log('skip due to lv_max')
            return False
        if w['lock_flg']:
            # self.log('skip due to lock_flg')
            return False
        if self.get_item_rank(w) > max_rank:
            self.log('skip due to max_rank')
            return False
        if w['rarity_value'] > max_rarity:
            self.log('skip due to max_rarity')
            return False
        if w['set_chara_id'] != 0:
            return False
        for i in self.get_item_innocents(w):
            if i and i['effect_rank'] > max_innocent_rank:
                self.log('skip due to max_innocent_rank')
                return False
            if i['innocent_type'] > max_innocent_type:
                self.log('skip due to max_innocent_type')
                return False
        if only_max_lvl and w['lv'] < w['lv_max']:
            return False
        return True
