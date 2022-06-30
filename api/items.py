from abc import ABCMeta
from data import data as gamedata

class Items(metaclass=ABCMeta):
    
    def __init__(self):
        super().__init__()

    def remove_innocents(self, e):
        innos = self.get_item_innocents(e)
        if len(innos) > 0:
            ids = []
            for i in innos:
                ids.append(i['id'])
            data = self.rpc("innocent/remove_all", {"t_innocent_ids": ids, "cost": 0})
            if data['result']['after_t_data']:
                self.update_equip_detail(e)
                for i in data['result']['after_t_data']['innocents']:
                    self.update_innocent(i)
            return data
        return {}

    def get_weapon_by_id(self, eid):
        for w in self.weapons:
            if w['id'] == eid:
                return w
        return None

    def get_equipment_by_id(self, eid):
        for w in self.equipments:
            if w['id'] == eid:
                return w
        return None

    def get_innocent_by_id(self, iid):
        for inno in self.innocents:
            if inno['id'] == iid:
                return inno
        return None

    def getEquip(self, i):
        for s in gamedata['equip']:
            if i == s['id']:
                return s

    def getWeapon(self, i):
        for s in gamedata['weapon']:
            if i == s['id']:
                return s
    
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
    
    def update_equip_detail(self, e, innos=[]):
        equip_type = 1 if self.get_weapon_by_id(e['id']) else 2
        data = self.rpc("player/update_equip_detail", {
            't_equip_id': e['id'],
            'equip_type': equip_type,
            'lock_flg': e['lock_flg'],
            'innocent_auto_obey_flg': e['innocent_auto_obey_flg'],
            'change_innocent_list': innos
        })
        if 't_weapon' in data['result']:
            index = self.weapons.index(e)
            self.weapons[index] = data['result']['t_weapon']
        elif 't_equipment' in data['result']:
            index = self.equipments.index(e)
            self.equipments[index] = data['result']['t_equipment']
        else:
            self.log("unable to update item with id: {0}".format(e['id']))

    def update_innocent(self, inno):
        old_inno = self.get_innocent_by_id(inno['id'])
        index = self.innocents.index(old_inno)
        self.innocents[index] = inno

    # e can be an equipment id or actual equipment/weapon
    def get_item_innocents(self, e):
        if isinstance(e, int):
            place_id = e
        elif 'm_weapon_id' in e:
            place_id = e['id']
        elif 'm_equipment_id' in e:
            place_id = e['id']
        elif 'id' in e:
            place_id = e['id']
        else:
            raise Exception('unable to determine item id')
        
        self.player_innocent_get_all(False)
        equipment_innocents = []
        for i in self.innocents:
            if i['place_id'] == place_id:
                equipment_innocents.append(i)
        return equipment_innocents

    def initInnocentPerEquipment(self, minimumEffectRank=7):
        #self.log('retrieving full list of innocents...')
        innocents = self.player_innocent_get_all(True)
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
    
    def can_item_be_sold(self, item, max_innocent_rank, max_item_rank, max_rarity):
        return self.filter_item(item, True, max_innocent_rank, max_item_rank, max_rarity, False)

    def can_item_be_donated(self, item, max_innocent_rank, max_item_rank, max_rarity):
        return self.filter_item(item, False, max_innocent_rank, max_item_rank, max_rarity, True)

    def filter_item(self, item, keep_max_lvl, max_innocent_rank, max_item_rank, max_rarity, only_max_lvl):
        if keep_max_lvl and item['lv'] == item['lv_max']:
            return False
        if item['lock_flg']:
            return False
        if self.get_item_rank(item) > max_item_rank:
            return False
        if item['rarity_value'] > max_rarity:
            return False
        if item['set_chara_id'] != 0:
            return False
        for inno in self.get_item_innocents(item):
            if inno and inno['effect_rank'] > max_innocent_rank:
                return False
            # TODO Keep specific innocent types?
            # for i in []: # innocents to keep
            #     if(i == item['m_innocent_id']) :
            #         print ("Element Exists")
            #         return False
        if only_max_lvl and item['lv'] < item['lv_max']:
            return False
        return True
