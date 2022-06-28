from abc import ABCMeta

from api.constants import Constants

class EtnaResort(metaclass=ABCMeta):
    
    def __init__(self):
        super().__init__()

    def breeding_center_list(self):
        data = self.rpc('breeding_center/list', {})
        return data
    
    def kingdom_weapon_equipment_entry(self, weap_ids=[], equip_ids=[]):
        data = self.rpc("kingdom/weapon_equipment_entry", {'t_weapon_ids': weap_ids, 't_equipment_ids': equip_ids})
        if len(weap_ids) > 0:
            self.player_weapons_get_all(True)
        if len(equip_ids) > 0:
            self.player_equipments_get_all(True)
        return data

    def kingdom_innocent_entry(self, innocent_ids=[]):
        data = self.rpc("kingdom/innocent_entry", {'t_innocent_ids': innocent_ids})
        self.player_innocents(updated_at=0, page=1)
        return data

    # takes arrays with ids for weapons and equips to retrieve from ER Deposit
    def breeding_center_pick_up(self, t_weapon_ids, t_equipment_ids):
        data = self.rpc('breeding_center/pick_up', {"t_weapon_ids":t_weapon_ids,"t_equipment_ids":t_equipment_ids})
        return data

    # takes arrays with ids for weapons and equips to add to ER Deposit
    def breeding_center_entrust(self, t_weapon_ids, t_equipment_ids):
        data = self.rpc('breeding_center/entrust', {"t_weapon_ids":t_weapon_ids,"t_equipment_ids":t_equipment_ids})
        return data

    #Checks if any item is fully leveled
    # If item is locked, has rare innocents or is legend, it will be retrieved
    # Otherwise it will be donated
    # Fill depository with items with rare innocents if possible, it not any r40 item
    def etna_resort_check_deposit_status(self, min_innocent_rank=5, min_item_rank=40):
        print("\nChecking state of item depository...")
        depository_data = self.breeding_center_list()
        items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
        deposit_free_slots = 11 - len(items_in_depository)
        weapons_to_retrieve =[]
        equipments_to_retrieve =[]
        weapons_to_donate =[]
        equipments_to_donate =[]
        finished_item_count = 0
        for i in items_in_depository:
            isWeapon = 'm_weapon_id' in i
            if(i['lv'] == i['lv_max']):
                finished_item_count+=1
                if isWeapon:
                    item =  self.getWeapon(i['m_weapon_id'])
                else:
                    item = self.getEquip(i['m_equipment_id'])

                innos_to_keep = [x for x in self.get_item_innocents(i['id']) if x['effect_rank'] >= min_innocent_rank]
                
                #Keep if rare innocent, item is locked or is legendary
                if(len(innos_to_keep) >0 or i['lock_flg'] or i['rarity_value'] > 70):
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

        if(total_to_donate > 0):
            result = self.kingdom_weapon_equipment_entry(weapons_to_donate, equipments_to_donate)

        depository_data = self.breeding_center_list()
        items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
        deposit_free_slots = 11 - len(items_in_depository)
        if(deposit_free_slots > 0):
            print(f"\tFinished retrieving equipment - {deposit_free_slots} slots available in repository")  
            self.etna_resort_fill_depository(deposit_free_slots, min_innocent_rank, min_item_rank)

        print(f"Finished checking depository.")  

    # Will first try to fill the depository with items with rare innocents (any rank)
    # Rest of spots will be filled with any item of specified rank (r40 by default)
    def etna_resort_fill_depository(self, deposit_free_slots=0, min_innocent_rank=5, min_item_rank=40):
        if(deposit_free_slots == 0):
            depository_data = self.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)
        
        if(deposit_free_slots > 0):
            print(f"\tFilling depository with {deposit_free_slots} items...") 
            #Fill depository with items that have rare innocents first, regrdless of item rank    
            self.etna_resort_find_items_for_depository(deposit_free_slots, min_innocent_rank, 0)

            #if slots available, fill with any item of specified rank
            depository_data = self.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)
            if(deposit_free_slots > 0):
                self.etna_resort_find_items_for_depository(deposit_free_slots, 0, min_item_rank)

    # Look for items with specified criteria
    def etna_resort_find_items_for_depository(self, deposit_free_slots=0, min_innocent_rank=5, min_item_rank=40):
        if(deposit_free_slots == 0):
            depository_data = self.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)
        
        if(deposit_free_slots > 0):    
            self.player_weapons_get_all()
            self.player_equipments_get_all()
            weapons_to_deposit =[]
            equipments_to_deposit =[]
            weapons_lvl1 = [x for x in self.weapons if x['lv'] <= 1 and x['set_chara_id'] == 0]
            equips_lvl1 = [x for x in self.equipments if x['lv'] <= 1 and x['set_chara_id'] == 0]
            
            weapons_to_deposit = self.generate_array_for_deposit(weapons_lvl1, deposit_free_slots, min_innocent_rank, min_item_rank)                 
            # If deposit cannot be filled with only weapons, find equipment to finish filling
            if(len(weapons_to_deposit) < deposit_free_slots):
                deposit_free_slots = deposit_free_slots - len(weapons_to_deposit)
                equipments_to_deposit = self.generate_array_for_deposit(equips_lvl1, deposit_free_slots, min_innocent_rank, min_item_rank)

            if(len(weapons_to_deposit) > 0 or len(equipments_to_deposit) > 0):
                self.breeding_center_entrust(weapons_to_deposit, equipments_to_deposit)

    def generate_array_for_deposit(self, all_items, deposit_free_slots, min_innocent_rank, min_item_rank):
        deposit_count=0
        items_to_deposit =[]
        for item in all_items:
            # If looking for rare innocents
            if(min_innocent_rank > 0):
                item_innocents  = self.get_item_innocents(item['id'])
                rare_innocents = [x for x in item_innocents if x['effect_rank'] >= min_innocent_rank]
                if(len(rare_innocents) > 0):
                    items_to_deposit.append(item['id'])
                    deposit_count+=1
                    if(deposit_count == deposit_free_slots):
                        return items_to_deposit
            #Otherwise look for rank
            else:
                item_rank = self.get_item_rank(item)
                if(item_rank >= min_item_rank):
                    items_to_deposit.append(item['id'])
                    deposit_count+=1
                    if(deposit_count == deposit_free_slots):
                        return items_to_deposit
        return items_to_deposit