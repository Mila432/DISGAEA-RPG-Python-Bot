from api.base import Base


class Player(Base):
    def __init__(self):
        super().__init__()
        self.deck = None
        self.weapons = []
        self.equipments = []

    def player_sync(self):
        data = self.rpc('player/sync', {})
        return data

    def player_tutorial_gacha_single(self):
        data = self.rpc('player/tutorial_gacha_single', {})
        return data

    def player_tutorial_choice_characters(self):
        data = self.rpc('player/tutorial_choice_characters', {})
        return data

    def player_characters(self, updated_at=None, page=None):
        data = self.rpc('player/characters', {"updated_at": updated_at, "page": page})
        return data

    def player_weapons(self, updated_at=0, page=1):
        if not hasattr(self, 'equipments'):
            self.weapons = []
        data = self.rpc('player/weapons', {"updated_at": updated_at, "page": page})
        if len(data['result']['_items']) <= 0:    return data
        self.weapons = self.weapons + data['result']['_items']
        return self.player_weapons(updated_at, page + 1)

    def player_weapon_effects(self, updated_at, page):
        data = self.rpc('player/weapon_effects', {"updated_at": updated_at, "page": page})
        return data

    def player_equipments(self, updated_at=0, page=1):
        if not hasattr(self, 'equipments'):
            self.equipments = []
        data = self.rpc('player/equipments', {"updated_at": updated_at, "page": page})
        if len(data['result']['_items']) <= 0:    return data
        self.equipments = self.equipments + data['result']['_items']
        return self.player_equipments(updated_at, page + 1)

    def player_equipment_effects(self, updated_at, page):
        data = self.rpc('player/equipment_effects', {"updated_at": updated_at, "page": page})
        return data

    def player_innocents(self, updated_at, page):
        data = self.rpc('player/innocents', {"updated_at": updated_at, "page": page})
        return data

    def player_clear_stages(self, updated_at, page):
        data = self.rpc('player/clear_stages', {"updated_at": updated_at, "page": page})
        return data

    def player_index(self):
        data = self.rpc('player/index', {})
        return data

    def player_agendas(self):
        data = self.rpc('player/agendas', {})
        return data

    def player_boosts(self):
        data = self.rpc('player/boosts', {})
        return data

    def player_character_collections(self):
        data = self.rpc('player/character_collections', {})
        return data

    def player_decks(self):
        data = self.rpc('player/decks', {})
        self.deck = [data['result']['_items'][self.t_deck_no]['t_character_ids'][x] for x in
                     data['result']['_items'][self.t_deck_no]['t_character_ids']]
        return data

    def player_home_customizes(self):
        data = self.rpc('player/home_customizes', {})
        return data

    def player_items(self):
        data = self.rpc('player/items', {})
        self.items = data['result']['_items']
        return data

    def player_stone_sum(self):
        data = self.rpc('player/stone_sum', {})
        self.log(
            'free stones:%s paid stones:%s' % (data['result']['_items'][0]['num'], data['result']['_items'][1]['num']))
        self.gems = data['result']['_items'][0]['num']
        return data

    def player_sub_tutorials(self):
        data = self.rpc('player/sub_tutorials', {})
        return data

    def player_gates(self):
        data = self.rpc('player/gates', {})
        return data

    def player_character_mana_potions(self):
        data = self.rpc('player/character_mana_potions', {})
        return data

    def player_tutorial(self, charaIdList=None, step=None, charaRarityList=None, name=None, gacha_fix=None):
        if charaIdList is None:
            data = self.rpc('player/tutorial', {})
        else:
            data = self.rpc('player/tutorial',
                            {"charaIdList": charaIdList, "step": step, "charaRarityList": charaRarityList, "name": name,
                             "gacha_fix": gacha_fix})
        return data

    def player_update_device_token(self, device_token):
        data = self.rpc('player/update_device_token',
                        {"device_token": "{length=32,bytes=0x034e8400c0f9937e142a2d2388845780...ef6bb16672be3d4a}"})
        return data

    def player_add(self):
        data = self.rpc('player/add', {})
        return data

    def player_badge_homes(self):
        data = self.rpc('player/badge_homes', {})
        return data

    def player_badges(self):
        data = self.rpc('player/badges', {})
        return data
