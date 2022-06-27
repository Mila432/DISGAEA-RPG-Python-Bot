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

    def shop_sell_equipment(self, sell_equipments):
        data = self.rpc('shop/sell_equipment',
                        {"sell_equipments": sell_equipments})
        return data