from data import data as gamedata


class GameData:
    def __init__(self):
        self.stages = gamedata['stages']
        self.items = gamedata['items']
        self.units = gamedata['units']
        self.characters = gamedata['characters']
        self.stages = gamedata['stages']
        self.weapons = gamedata['weapon']
        self.equipment = gamedata['equip']
        self.innocent_types = gamedata['innocent_types']

    def get_equipment(self, i):
        for w in self.equipment:
            if w['id'] == i:
                return w
        return None

    def get_weapon(self, i):
        for w in self.weapons:
            if w['id'] == i:
                return w
        return None

    def get_stage(self, i):
        i = int(i)
        for s in self.stages:
            if i == s['id']:
                return s

    def get_item(self, i):
        for s in self.items:
            if i == s['id']:
                return s

    def get_unit(self, i):
        for s in self.units:
            if i == s['id']:
                return s

    def get_character(self, i):
        for s in self.characters:
            if i == s['id']:
                return s

    def get_item_rank(self, e):
        item_rank = 140
        if 'm_weapon_id' in e:
            weapon = self.get_weapon(e['m_weapon_id'])
            if weapon is not None:
                item_rank = weapon['item_rank']
        elif 'm_equipment_id' in e:
            equip = self.get_equipment(e['m_equipment_id'])
            if equip is not None:
                item_rank = equip['item_rank']
        elif 'item_rank' in e:
            item_rank = e['item_rank']
        else:
            raise Exception('unable to determine item rank')
        if item_rank > 100:
            item_rank = item_rank - 100
        return item_rank
