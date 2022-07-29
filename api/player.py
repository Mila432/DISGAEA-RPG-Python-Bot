from api.base import Base


class Player(Base):
    def __init__(self):
        super().__init__()

    def player_characters(self, refresh=False):
        if len(self.pd.characters) > 0 and not refresh:
            return self.pd.characters
        self.pd.characters = []
        self.logger.debug("refreshing player characters...")

        page_index = 1
        iterate_next_page = True
        while iterate_next_page:
            data = self.client.player_characters(updated_at=0, page=page_index)
            if len(data['result']['_items']) <= 0:
                iterate_next_page = False
            self.pd.characters = self.pd.characters + data['result']['_items']
            page_index += 1

        return self.pd.characters

    def player_character_collections(self, refresh=False):
        if len(self.pd.character_collections) > 0 and not refresh:
            return self.pd.character_collections
        self.pd.character_collections = []
        self.logger.debug("refreshing player character collections...")
        data = self.client.player_character_collections()
        self.pd.character_collections = data['result']['_items']
        return self.pd.character_collections

    def player_weapons(self, refresh=False):
        if len(self.pd.weapons) > 0 and not refresh:
            return self.pd.weapons
        self.pd.weapons = []
        self.logger.debug("refreshing player weapons...")
        page_index = 1
        iterate_next_page = True
        while iterate_next_page:
            data = self.client.player_weapons(updated_at=0, page=page_index)
            if len(data['result']['_items']) <= 0:
                iterate_next_page = False
            self.pd.weapons = self.pd.weapons + data['result']['_items']
            page_index += 1
        return self.pd.weapons

    def player_equipment(self, refresh=False):
        if len(self.pd.equipment) > 0 and not refresh:
            return self.pd.equipment
        self.pd.equipment = []
        self.logger.debug("refreshing player equipments...")

        page_index = 1
        iterate_next_page = True
        while iterate_next_page:
            data = self.client.player_equipments(updated_at=0, page=page_index)
            if len(data['result']['_items']) <= 0:
                iterate_next_page = False
            self.pd.equipment = self.pd.equipment + data['result']['_items']
            page_index += 1
        return self.pd.equipment

    def player_innocents(self, refresh=False):
        if len(self.pd.innocents) > 0 and not refresh:
            return self.pd.innocents
        self.pd.innocents = []
        self.logger.debug("refreshing player innocents...")

        page_index = 1
        iterate_next_page = True
        while iterate_next_page:
            data = self.client.player_innocents(updated_at=0, page=page_index)
            if len(data['result']['_items']) <= 0:
                iterate_next_page = False
            self.pd.innocents = self.pd.innocents + data['result']['_items']
            page_index += 1
        return self.pd.innocents

    def player_decks(self, refresh=False):
        if len(self.pd.decks) > 0 and not refresh:
            return self.pd.decks
        data = self.client.player_decks()
        self.pd.decks = data['result']['_items']
        return self.pd.decks

    def player_items(self, refresh=False):
        if len(self.pd.items) > 0 and not refresh:
            return self.pd.items
        self.pd.items = []
        self.logger.debug("refreshing player items...")

        page_index = 1
        iterate_next_page = True
        while iterate_next_page:
            data = self.client.player_items(updated_at=0, page=page_index)
            if len(data['result']['_items']) <= 0:
                iterate_next_page = False
            self.pd.items = self.pd.items + data['result']['_items']
            page_index += 1
        return self.pd.innocents

    def player_stone_sum(self):
        data = self.client.player_stone_sum()
        self.log('free stones:%s paid stones:%s' % (
            data['result']['_items'][0]['num'],
            data['result']['_items'][1]['num']))
        self.pd.gems = data['result']['_items'][0]['num']
        return data

    def char_stage_info(self, unit_id, use_cache=False):
        self.log("Looking for character stage info, with id: %s" % unit_id)
        m_character_id = 0
        for i in self.pd.characters:
            if i['id'] == unit_id:
                m_character_id = i['m_character_id']
                break

        if len(self.pd.character_collections) <= 0 or use_cache is False:
            self.player_character_collections(refresh=True)

        c = next((x for x in self.pd.character_collections if x['m_character_id'] == m_character_id), None)
        return c

    # Updates equipment with innocents list
    def player_update_equip_detail(self, e, innos=None):
        if innos is None:
            innos = []
        data = self.client.player_update_equip_detail(e, innos)
        self.pd.update_equip(data['result'])
