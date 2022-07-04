from abc import ABCMeta

from api.constants import Constants, Innocent_Training_Result

class EtnaResort(metaclass=ABCMeta):
    
    def __init__(self):
        super().__init__()

    def breeding_center_list(self):
        data = self.rpc('breeding_center/list', {})
        return data
    
    #Donate equipments
    def kingdom_weapon_equipment_entry(self, weap_ids=[], equip_ids=[]):
        data = self.rpc("kingdom/weapon_equipment_entry", {'t_weapon_ids': weap_ids, 't_equipment_ids': equip_ids})
        if len(weap_ids) > 0:
            self.player_weapons_get_all(True)
        if len(equip_ids) > 0:
            self.player_equipments_get_all(True)
        return data

    # Donate innocents
    def kingdom_innocent_entry(self, innocent_ids=[]):
        data = self.rpc("kingdom/innocent_entry", {'t_innocent_ids': innocent_ids})
        self.player_innocent_get_all(True)
        return data

    # takes arrays with ids for weapons and equips to retrieve from ER Deposit
    def breeding_center_pick_up(self, t_weapon_ids, t_equipment_ids):
        data = self.rpc('breeding_center/pick_up', {"t_weapon_ids":t_weapon_ids,"t_equipment_ids":t_equipment_ids})
        return data

    # takes arrays with ids for weapons and equips to add to ER Deposit
    def breeding_center_entrust(self, t_weapon_ids, t_equipment_ids):
        data = self.rpc('breeding_center/entrust', {"t_weapon_ids":t_weapon_ids,"t_equipment_ids":t_equipment_ids})
        return data

    def etna_resort_refine(self, item_type, id):
        data = self.rpc('weapon_equipment/rarity_up', {"item_type":item_type,"id":id})
        return data
    
    # Looks for maxed items retrieves or donates them and fills it again
    def etna_resort_check_deposit_status(self, max_innocent_rank=5, min_item_rank=40, max_item_rarity =40):
        print("\nChecking state of item depository...")
        
        self.etna_resort_retrieve_or_donate_items_from_depository(max_innocent_rank, min_item_rank, max_item_rarity)

        depository_data = self.breeding_center_list()
        items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
        deposit_free_slots = 11 - len(items_in_depository)
        if(deposit_free_slots > 0):
            print(f"\tFinished retrieving equipment - {deposit_free_slots} slots available in repository")  
            self.etna_resort_fill_depository(deposit_free_slots, max_innocent_rank, min_item_rank)

        print(f"Finished checking depository.")  

    # Checks if any item is fully leveled
    # If item is locked, has rare innocents or is above specified rarity (default rare), it will be retrieved
    # Otherwise it will be donated
    # If there is no invetory space to retrieve, sell 20 items and retry
    def etna_resort_retrieve_or_donate_items_from_depository(self, max_innocent_rank=5, max_item_rank=40, max_item_rarity = 40):
        retry = True
        
        # execute once - repeat if there was an exception retrieving equipment
        while retry:
            retry = False

            depository_data = self.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            weapons_to_retrieve =[]
            equipments_to_retrieve =[]
            weapons_to_donate =[]
            equipments_to_donate =[]
            finished_item_count = 0

            for i in items_in_depository:
                isWeapon = 'm_weapon_id' in i
                if(i['lv'] == i['lv_max']):
                    finished_item_count+=1
                    innos_to_keep = [x for x in self.get_item_innocents(i['id']) if x['effect_rank'] >= max_innocent_rank]                
                    #Keep if rare innocent, item is locked or is above rarity
                    if(len(innos_to_keep) >0 or i['lock_flg'] or i['rarity_value'] > max_item_rarity):
                        #TODO check if slots available for retrieving?
                        if(isWeapon):
                            weapons_to_retrieve.append(i['id'])
                        else:
                            equipments_to_retrieve.append(i['id'])
                    else:
                        if(isWeapon):
                            weapons_to_donate.append(i['id'])
                        else:
                            equipments_to_donate.append(i['id'])

            total_to_donate = len(weapons_to_donate) + len(equipments_to_donate)
            total_to_retrieve = len(weapons_to_retrieve) + len(equipments_to_retrieve) 
            if(finished_item_count > 0):
                print(f"\tFinished leveling {finished_item_count} equipments - {total_to_retrieve} will be retrieved, {total_to_donate} will be donated")
            
            if(total_to_retrieve > 0):
                result = self.breeding_center_pick_up(weapons_to_retrieve, equipments_to_retrieve)
                
                if(result['error'] == 'Maximum armour slot reached' or result['error'] == 'Maximum weapon slot reached'):
                    sell_equipments = result['error'] == 'Maximum armour slot reached'
                    sell_weapons = result['error'] == 'Maximum weapon slot reached'
                    self.shop_free_inventory_space(sell_weapons, sell_equipments, 20)
                    retry = True

            if(total_to_donate > 0):
                result = self.kingdom_weapon_equipment_entry(weapons_to_donate, equipments_to_donate)

    # Will first try to fill the depository with items with rare innocents (any rank)
    # Rest of spots will be filled with any item of specified rank (r40 by default)
    def etna_resort_fill_depository(self, deposit_free_slots=0, max_innocent_rank=5, max_item_rank=40):
        if(deposit_free_slots == 0):
            depository_data = self.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)
        
        if(deposit_free_slots > 0):
            print(f"\tFilling depository with {deposit_free_slots} items...") 
            #Fill depository with items that have rare innocents first, regrdless of item rank    
            self.etna_resort_find_items_for_depository(deposit_free_slots, max_innocent_rank, 0)

            #if slots available, fill with any item of specified rank
            depository_data = self.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)
            if(deposit_free_slots > 0):
                self.etna_resort_find_items_for_depository(deposit_free_slots, 0, max_item_rank)

    # Look for items with specified criteria
    def etna_resort_find_items_for_depository(self, deposit_free_slots=0, max_innocent_rank=5, max_item_rank=40):
        if(deposit_free_slots == 0):
            depository_data = self.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)
        
        if(deposit_free_slots > 0):    
            self.player_weapons_get_all(True)
            self.player_equipments_get_all(True)
            weapons_to_deposit =[]
            equipments_to_deposit =[]
            weapons_lvl1 = [x for x in self.weapons if x['lv'] <= 1 and x['set_chara_id'] == 0]
            equips_lvl1 = [x for x in self.equipments if x['lv'] <= 1 and x['set_chara_id'] == 0]

            equipments_to_deposit = self.generate_array_for_deposit(equips_lvl1, deposit_free_slots, max_innocent_rank, max_item_rank)
            
            # If deposit cannot be filled with only equipment, find weapons to finish filling
            if(len(equipments_to_deposit) < deposit_free_slots):
                deposit_free_slots = deposit_free_slots - len(equipments_to_deposit)
                weapons_to_deposit = self.generate_array_for_deposit(weapons_lvl1, deposit_free_slots, max_innocent_rank, max_item_rank)                 
            
            if(len(weapons_to_deposit) > 0 or len(equipments_to_deposit) > 0):
                self.breeding_center_entrust(weapons_to_deposit, equipments_to_deposit)

    def generate_array_for_deposit(self, all_items, deposit_free_slots, max_innocent_rank, max_item_rank, max_rarity = 40):
        deposit_count=0
        items_to_deposit =[]
        filled = False
        innocent_count = 0

        while not filled:
            for item in all_items:
                # If looking for rare innocents
                item_innocents  = self.get_item_innocents(item['id'])
                if(max_innocent_rank > 0):                
                    rare_innocents = [x for x in item_innocents if x['effect_rank'] >= max_innocent_rank]
                    if(len(rare_innocents) > 0):
                        items_to_deposit.append(item['id'])
                        deposit_count+=1
                        if(deposit_count == deposit_free_slots):
                            filled = True
                            return items_to_deposit
                    filled = True
                
                # Otherwise fill with commons of specific rank
                # fill with items with no innocents first, if there aren't enough items with 1 and so on
                else:
                    item_rank = self.get_item_rank(item)
                    if(item_rank >= max_item_rank and item['rarity_value'] > max_rarity):
                        continue
                    if(len(item_innocents) > innocent_count): continue
                    items_to_deposit.append(item['id'])
                    deposit_count+=1
                    if(deposit_count == deposit_free_slots):
                        filled = True
                        return items_to_deposit
                    innocent_count += 1
        return items_to_deposit

    def etna_donate_innocents(self, max_innocent_rank=8, max_innocent_type=8):
        self.player_innocents()
        innos = []
        skipping = 0
        for i in self.innocents:
            if not self._filter_innocent(i, max_innocent_rank, max_innocent_type):
                skipping += 1
                continue
            innos.append(i['id'])

        self.log('donate - skipping %s innocents' % skipping)
        if len(innos) > 0:
            for batch in (innos[i:i + 20] for i in range(0, len(innos), 20)):
                self.kingdom_innocent_entry(innocent_ids=batch)

    def etna_resort_donate_items(self,max_innocent_rank=5, max_item_rank=40, max_rarity=40):
        print("\nLooking for items to donate...")
        self.player_equipments_get_all(True)
        self.player_weapons_get_all(True)
        self.player_innocent_get_all(True)

        weapons_to_donate = []
        equipments_to_donate = []

        all_weapons = [x for x in self.weapons if x['lv'] == x['lv_max'] and x['rarity_value'] < max_rarity]
        all_equipments = [x for x in self.equipments if x['lv'] == x['lv_max'] and x['rarity_value'] < max_rarity]

        for item in all_weapons:
            if(self.can_item_be_donated(item, max_innocent_rank, max_item_rank, max_rarity)):
                weapons_to_donate.append(item['id'])

        for item in all_equipments:
            if(self.can_item_be_donated(item, max_innocent_rank, max_item_rank, max_rarity)):
                equipments_to_donate.append(item['id'])

        print(f"\tWill donate {len(weapons_to_donate)} weapons and {len(equipments_to_donate)} equipments")
        # TODO: remove rare innocents?
        # for item in items_to_donate:
        #     self.log_donate(e)
        #     try:
        #         self.remove_innocents(e)
        #     except:
        #         e = None  

        # selling, skipping = self.filter_items(False, max_innocent_rank, max_innocent_type, max_rank, max_rarity, True)
        # self.log('donate - skipping %s items' % skipping)
        # if len(selling) > 0:
        #     for i in selling:
        #         e = self.get_equipment_by_id(i['eqid']) or self.get_weapon_by_id(i['eqid'])
        #         self.log_donate(e)
        #         try:
        #             self.remove_innocents(e)
        #             items.append(i['eqid'])
        #         except:
        #             e = None

        for weapon_batch in (weapons_to_donate[i:i + 20] for i in range(0, len(weapons_to_donate), 20)):
            self.kingdom_weapon_equipment_entry(weap_ids=weapon_batch)

        for equipment_batch in (equipments_to_donate[i:i + 20] for i in range(0, len(equipments_to_donate), 20)):
            self.kingdom_weapon_equipment_entry(equip_ids=equipment_batch)

        print("\tFinished donating equipment")

    def etna_resort_refine_weapon(self, weapon_id):
        retry = True
        print("Attempting to refine equipment...")
        attempt_count = 0
        result = ''
        while retry:
            attempt_count +=1
            res = self.etna_resort_refine(3, weapon_id)
            if 'success_type' in res['result']:
                result = res['result']['success_type']
                retry = False
        print(f"\tRefined weapon. Attempts used {attempt_count}. Result: {result}")

    def etna_resort_refine_equipment(self, equipment_id):
        retry = True
        print("Attempting to refine equipment...")
        attempt_count = 0
        result = ''
        while retry:
            attempt_count +=1
            res = self.etna_resort_refine(4, equipment_id)
            if 'success_type' in res['result']:
                result = res['result']['success_type']
                retry = False
        print(f"\tRefined equipment. Attempts used {attempt_count}. Result: {result}")

    def etna_resort_innocent_training(self, t_innocent_id):
        data = self.rpc('innocent/training', {"t_innocent_id":t_innocent_id})
        return data

    def innocent_get_training_result(self, training_result):
        if (training_result == Innocent_Training_Result.NORMAL):
            return "Normal"
        if (training_result == Innocent_Training_Result.NOT_BAD):
            return "Not bad"
        if (training_result == Innocent_Training_Result.DREAMLIKE):
            return "Dreamlike"
            
    def log_donate(self, w):
        item = self.getWeapon(w['m_weapon_id']) if 'm_weapon_id' in w else self.getEquip(w['m_equipment_id'])
        self.log(
            '[-] donate item: "%s" rarity: %s rank: %s lv: %s lv_max: %s locked: %s' %
            (item['name'], w['rarity_value'], self.get_item_rank(w), w['lv'],
             w['lv_max'], w['lock_flg'])
        )