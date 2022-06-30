from abc import ABCMeta

class Shop(metaclass=ABCMeta):
    
    def __init__(self):
        super().__init__()

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

    def shop_sell_equipment(self, sell_equipments):
        data = self.rpc('shop/sell_equipment',
                        {"sell_equipments": sell_equipments})
        return data

    def shop_buy_item(self, itemid, quantity):
        data = self.rpc('shop/buy_item', {"id": itemid, "quantity": quantity})
        return data

    def shop_change_equipment_items(self, shop_rank=32):
        updateNumber = self.shop_equipment_shop()['result']['lineup_update_num']
        if (updateNumber < 5):
            data = self.rpc('shop/change_equipment_items', {"shop_rank": shop_rank})
        else:
            self.log('Free refreshes used up already')
            data = 0
        return data

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

    def BuyAllEquipmentWithInnocents(self, shop_rank):
        print("\nBuying all equipment with innocents...")  
        buy = True
        
        while buy:
            equipment_items = self.shop_equipment_items()['result']['_items']      
            for i in equipment_items:
                if i['sold_flg']: continue
                if i['innocent_num'] > 0:
                    itemIDs = []
                    itemIDs.append(i['id']) 
                    res = self.shop_buy_equipment(item_type=i['item_type'], itemids=itemIDs)
                    if (res['error'] == 'Maximum weapon slot reached' or res['error'] == 'Maximum armour slot reached'):
                        buy = False
            if(buy):
                updateNumber = self.shop_equipment_shop()['result']['lineup_update_num']
                if (updateNumber < 5):
                    print(f"\tRefreshing Shop. Current Refresh: {updateNumber}")
                    data = self.rpc('shop/change_equipment_items', {"shop_rank": shop_rank})
                else:
                    print(f"\tFree shop refreshes used up. Finished buying all equipment.")
                    buy = False

    def sell_r40_equipment_with_no_innocents(self):
        print("\nLooking for r40 equipment with no innocents to sell...")
        self.player_equipments_get_all(True)
        self.player_weapons_get_all(True)
        self.player_innocent_get_all(True)
        selling = []
        wc=0
        ec=0
        for w in self.weapons:
            wId = w['id']
            if self.get_item_rank(w) < 40: continue
            if w['set_chara_id'] != 0: continue
            if w['lv'] > 1: continue
            if w['lock_flg'] == True: continue
            if(len(self.get_item_innocents(wId)) == 0):
                wc+=1
                selling.append({'eqtype': 1, 'eqid': wId}) 
        for e in self.equipments:
            if self.get_item_rank(e) < 40: continue
            eId = e['id']
            if e['set_chara_id'] != 0: continue
            if e['lv'] > 1: continue
            if e['lock_flg'] == True: continue
            if(len(self.get_item_innocents(eId)) == 0):
                ec+=1
                selling.append({'eqtype': 2, 'eqid': eId})
        
        print(f"\tWeapons to sell: {wc} - Equipment to sell: {ec}\n")
        if(len(selling) > 0):            
            #self.shop_log_sale(w)
            self.shop_sell_equipment(selling)

    # Sell items (to make sure depository can be emptied) that have no innocent or 1 common
    def shop_free_inventory_space(self, sell_weapons=False, sell_equipment=False, item_to_sell = 20):
        print("\nSelling items to free inventory space...")
        selling = []
        wc=0
        ec=0

        self.player_equipments_get_all(True)
        self.player_weapons_get_all(True)
        self.player_innocent_get_all(True)

        if(sell_weapons):
            for w in self.weapons:
                wId = w['id']
                if self.get_item_rank(w) < 40: continue
                if w['set_chara_id'] != 0: continue
                if w['lv'] > 1: continue
                if w['lock_flg'] == True: continue
                if w['rarity_value'] >= 40: continue
                item_innocents = self.get_item_innocents(w['id'])
                innos_to_keep = [x for x in item_innocents if x['effect_rank'] >= 5]
                if(len(item_innocents) == 0 or (len(item_innocents) == 1 and len(innos_to_keep) == 0)):
                    wc+=1
                    selling.append({'eqtype': 1, 'eqid': wId}) 
                    if(wc == item_to_sell):
                        break

        if(sell_equipment):
            for e in self.equipments:
                if self.get_item_rank(e) < 40: continue
                eId = e['id']
                if e['set_chara_id'] != 0: continue
                if e['lv'] > 1: continue
                if e['lock_flg'] == True: continue
                if e['rarity_value'] >= 40: continue
                item_innocents = self.get_item_innocents(e['id'])
                innos_to_keep = [x for x in item_innocents if x['effect_rank'] >= 5]
                if(len(item_innocents) == 0 or (len(item_innocents) == 1 and len(innos_to_keep) == 0)):
                    ec+=1
                    selling.append({'eqtype': 2, 'eqid': eId})
                    if(ec == item_to_sell):
                        break
        
        print(f"\tWeapons to sell: {wc} - Equipment to sell: {ec}\n")
        if(len(selling) > 0):            
            #self.shop_log_sale(w)
            self.shop_sell_equipment(selling)
            
    def innocent_safe_sellItems(self, minimumEffectRank=5, minimumItemRank=32):
        self.player_equipments_get_all()
        self.player_weapons_get_all()
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

    def shop_log_sale(self, w):
        item = self.getWeapon(w['m_weapon_id']) if 'm_weapon_id' in w else self.getEquip(w['m_equipment_id'])
        self.log(
            '[-] sell item: "%s" rarity: %s rank: %s lv: %s lv_max: %s locked: %s' %
            (item['name'], w['rarity_value'], self.get_item_rank(w), w['lv'],
             w['lv_max'], w['lock_flg'])
        )