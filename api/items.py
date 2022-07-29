from api.shop import Shop


class Items(Shop):

    def can_item_be_sold(self, item, max_innocent_rank, max_item_rank, max_rarity):
        return self.pd.check_item(item, skip_max_lvl=True, max_innocent_rank=max_innocent_rank,
                                  max_item_rank=max_item_rank, max_rarity=max_rarity, only_max_lvl=False)

    def can_item_be_donated(self, item, max_innocent_rank, max_item_rank, max_rarity):
        return self.pd.check_item(item, skip_max_lvl=False, max_innocent_rank=max_innocent_rank,
                                  max_item_rank=max_item_rank, max_rarity=max_rarity, only_max_lvl=True)

    def remove_innocents(self, e):
        innos = self.pd.get_item_innocents(e)
        if len(innos) > 0:
            ids = []
            for i in innos:
                ids.append(i['id'])
            data = self.client.innocent_remove_all(ids, 0)
            if data['result']['after_t_data']:
                self.player_update_equip_detail(e)
                for i in data['result']['after_t_data']['innocents']:
                    self.pd.update_innocent(i)
            return data
        return {}
