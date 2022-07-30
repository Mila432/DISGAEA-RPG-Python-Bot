from abc import ABCMeta

from api.player import Player


class Shop(Player, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    def buy_daily_items_from_shop(self):
        product_data = self.client.shop_index()['result']['shop_buy_products']['_items']
        self.logger.info("Buying daily AP Pots and bribe items...")
        # 50% AP Pot
        item = [x for x in product_data if x['m_product_id'] == 102][0]
        if item['buy_num'] == 0:
            self.client.shop_buy_item(102, 2)
        # Golden candy
        item = [x for x in product_data if x['m_product_id'] == 107][0]
        if item['buy_num'] == 0:
            self.client.shop_buy_item(107, 3)
        # Golden Bar
        item = [x for x in product_data if x['m_product_id'] == 108][0]
        if item['buy_num'] == 0:
            self.client.shop_buy_item(108, 2)
        # Skip ticket
        item = [x for x in product_data if x['m_product_id'] == 1121][0]
        if item['buy_num'] == 0:
            self.client.shop_buy_item(1121, 1)

    def buy_all_equipment_with_innocents(self, shop_rank):
        self.log("Buying all equipment with innocents...")
        buy = True

        while buy:
            equipment_items = self.client.shop_equipment_items()['result']['_items']
            for i in equipment_items:
                if i['sold_flg']: continue
                if i['innocent_num'] > 0:
                    item_ids = [i['id']]
                    res = self.client.shop_buy_equipment(item_type=i['item_type'], itemids=item_ids)
                    if res['error'] == 'Maximum weapon slot reached' or res['error'] == 'Maximum armour slot reached':
                        buy = False
            if buy:
                update_number = self.client.shop_equipment_shop()['result']['lineup_update_num']
                if update_number < 5:
                    self.logger.info(f"Refreshing Shop. Current Refresh: {update_number}")
                    self.client.shop_change_equipment_items(shop_rank=shop_rank)
                else:
                    self.log(f"Free shop refreshes used up. Finished buying all equipment.")
                    buy = False

    def sell_r40_equipment_with_no_innocents(self):
        self.log("Looking for r40 equipment with no innocents to sell...")
        self.player_equipment(True)
        self.player_weapons(True)
        self.player_innocents(True)

        items, skipping = self.pd.filter_items(min_item_rank=40, max_item_level=1,
                                               skip_equipped=True, skip_locked=True)
        selling = []
        wc = 0
        ec = 0
        for item in items:
            _id = item['id']
            equip_type = self.pd.get_equip_type(item)
            if len(self.pd.get_item_innocents(_id)) == 0:
                if equip_type == 2:
                    ec += 1
                else:
                    wc += 1
                selling.append({'eqtype': equip_type, 'eqid': _id})

        self.log(f'Weapons to sell: {wc} - Equipment to sell: {ec}')

        if len(selling) > 0:
            for x in selling:
                self.log_sell(x)
            self.client.shop_sell_equipment(selling)

    # Sell items (to make sure depository can be emptied) that have no innocent or 1 common
    def shop_free_inventory_space(self, sell_weapons=False, sell_equipment=False, items_to_sell=20):
        self.log("Selling items to free inventory space...")
        selling = []
        wc = 0
        ec = 0

        self.player_equipment(True)
        self.player_weapons(True)
        self.player_innocents(True)

        items, skipping = self.pd.filter_items(
            min_item_rank=40, max_rarity=39, max_item_level=1,
            skip_equipped=True, skip_locked=True,
        )

        if sell_weapons:
            for item in items:
                _id = item['id']
                item_innocents = self.pd.get_item_innocents(item['id'])
                innos_to_keep = [x for x in item_innocents if x['effect_rank'] >= 5]
                if len(item_innocents) == 0 or (len(item_innocents) == 1 and len(innos_to_keep) == 0):
                    equip_type = self.pd.get_equip_type(item)
                    if equip_type == 2 and sell_equipment:
                        ec += 1
                        selling.append({'eqtype': equip_type, 'eqid': _id})
                    elif sell_weapons:
                        wc += 1
                        selling.append({'eqtype': equip_type, 'eqid': _id})

                    if len(selling) == items_to_sell:
                        break

        self.log(f"Weapons to sell: {wc} - Equipment to sell: {ec}")
        if len(selling) > 0:
            for x in selling:
                self.log_sell(x)
            self.client.shop_sell_equipment(selling)

    def initInnocentPerEquipment(self, minimum_effect_rank=7):
        innocents = self.player_innocents(True)
        equipment_innocents = {}
        if len(innocents) >= 1:
            self.log('generating equip-id => innocent hashmapmap...')
            for innocent in innocents:
                equipment_id = innocent['place_id']
                if equipment_id in equipment_innocents:
                    equipment_innocents[equipment_id]['innocentsArray'][innocent['place_no']] = innocent
                    # equipment_innocents[equipment_id][innocent['place_no']]=innocent # if we want an hasmap too...
                else:
                    equipment_innocents[equipment_id] = {}
                    equipment_innocents[equipment_id]['innocentsArray'] = [None] * 10
                    equipment_innocents[equipment_id]['innocentsArray'][innocent['place_no']] = innocent
                    # equipment_innocents[equipment_id][innocent['place_no']]=innocent # if we want an hasmap too...
                    equipment_innocents[equipment_id]['canSell'] = innocent['effect_rank'] < minimum_effect_rank
                if innocent['effect_rank'] >= minimum_effect_rank:
                    equipment_innocents[equipment_id]['canSell'] = False
            self.log('hashmap generated!')
        return equipment_innocents

    def innocent_safe_sell_items(self, min_effect_rank=5, min_item_rank=32):
        self.player_equipment(True)
        self.player_weapons(True)

        equipments = self.initInnocentPerEquipment(min_effect_rank)
        selling = []

        items, skipping = self.pd.filter_items(
            max_item_level=1, max_item_rank=min_item_rank,
            skip_equipped=True, skip_locked=True,
        )
        for item in items:
            _id = item['id']
            if _id in equipments and equipments[_id]['canSell']:
                continue
            equip_type = self.pd.get_equip_type(item)
            selling.append({'eqtype': equip_type, 'eqid': _id})

        if len(selling) > 0:
            for x in selling:
                self.log_sell(x)
            self.client.shop_sell_equipment(selling)

    def shop_use_all_tickets(self):
        tickets_left = True
        while tickets_left:
            data = self.client.shop_gacha()
            if data['result']['item_type'] == 4:
                item = self.gd.get_equipment(data['result']['item_id'])
            if data['result']['item_type'] == 3:
                item = self.gd.get_weapon(data['result']['item_id'])
            if data['result']['item_type'] not in (3, 4):
                item = self.gd.get_item(data['result']['item_id'])
            self.log(
                f"Obtained {data['result']['m_garapon_lot_id']} prize: {data['result']['item_num']} x {item['name']}")
            if data['result']['t_item_garapon']['num'] <= 0:
                tickets_left = False

    def sell_items(self, max_rarity=40, max_item_rank=100, keep_max_lvl=False, only_max_lvl=False, max_innocent_rank=10,
                   max_innocent_type=8):
        self.player_equipment(True)
        self.player_weapons(True)

        selling, skipping = self.pd.filter_items(
            skip_max_lvl=keep_max_lvl, max_innocent_rank=max_innocent_rank, max_innocent_type=max_innocent_type,
            max_item_rank=max_item_rank, max_rarity=max_rarity,
            only_max_lvl=only_max_lvl)

        self.log('skipping %s items, selling %s items' % (skipping, len(selling)))
        if len(selling) >= 1:
            sell_list = []
            for i in selling:
                sell_list.append({'eqtype': self.pd.get_equip_type(i), 'eqid': i['id']})
                self.log_sell(i)
            data = self.client.shop_sell_equipment(sell_list)
            self.check_resp(data)
            # self.player_weapons(True)
            # self.player_equipment(True)
            return data

    def log_sell(self, w):
        item = self.gd.get_weapon(w['m_weapon_id']) if 'm_weapon_id' in w else self.gd.get_weapon(w['m_equipment_id'])
        self.logger.debug(
            '[-] sell item: "%s" rarity: %s rank: %s lv: %s lv_max: %s locked: %s' %
            (item['name'], w['rarity_value'], self.gd.get_item_rank(w), w['lv'],
             w['lv_max'], w['lock_flg'])
        )
