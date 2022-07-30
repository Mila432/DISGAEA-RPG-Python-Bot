from abc import ABCMeta

from api.constants import Innocent_Training_Result
from api.items import Items


class EtnaResort(Items, metaclass=ABCMeta):

    def __init__(self):
        super().__init__()

    # def breeding_center_list(self):
    #     data = self.rpc('breeding_center/list', {})
    #     return data

    # Donate equipments
    def kingdom_weapon_equipment_entry(self, weapon_ids=[], equipment_ids=[]):
        data = self.client.kingdom_weapon_equipment_entry(weapon_ids, equipment_ids)
        if len(weapon_ids) > 0:
            self.player_weapons(True)
        if len(equipment_ids) > 0:
            self.player_equipment(True)
        return data

    # Donate innocents
    def kingdom_innocent_entry(self, innocent_ids=[]):
        data = self.client.kingdom_innocent_entry(innocent_ids)
        self.player_innocents(True)
        return data

    def etna_resort_get_all_daily_rewards(self):
        return self.client.trophy_get_reward_daily_request()

    # Looks for maxed items retrieves or donates them and fills it again
    def etna_resort_check_deposit_status(self, max_innocent_rank=5, max_item_rank_to_donate=40,
                                         max_item_rarity_to_donate=40, min_item_rank_to_deposit=40):
        self.log("Checking state of item depository...")

        self.etna_resort_retrieve_or_donate_items_from_depository(max_innocent_rank, max_item_rank_to_donate,
                                                                  max_item_rarity_to_donate)

        depository_data = self.client.breeding_center_list()
        items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
        deposit_free_slots = 11 - len(items_in_depository)
        if deposit_free_slots > 0:
            self.log(f"Finished retrieving equipment - {deposit_free_slots} slots available in repository")
            self.etna_resort_fill_depository(deposit_free_slots, max_innocent_rank, min_item_rank_to_deposit)

        self.log(f"Finished checking depository.")

        # Checks if any item is fully leveled

    # If item is locked, has rare innocents or is above specified rarity (default rare), it will be retrieved
    # Otherwise it will be donated
    # If there is no invetory space to retrieve, sell 20 items and retry
    def etna_resort_retrieve_or_donate_items_from_depository(self, max_innocent_rank=5, max_item_rank_to_donate=40,
                                                             max_item_rarity_to_donate=40):
        retry = True

        # execute once - repeat if there was an exception retrieving equipment
        while retry:
            retry = False

            depository_data = self.client.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            weapons_to_retrieve = []
            equipments_to_retrieve = []
            weapons_to_donate = []
            equipments_to_donate = []
            finished_item_count = 0

            for i in items_in_depository:
                item_rank = self.gd.get_item_rank(i)
                isWeapon = 'm_weapon_id' in i
                if i['lv'] == i['lv_max']:
                    finished_item_count += 1
                    innos_to_keep = [x for x in self.pd.get_item_innocents(i['id']) if
                                     x['effect_rank'] >= max_innocent_rank]
                    # Keep if rare innocent, item is locked or is above rarity
                    if (len(innos_to_keep) > 0 or i['lock_flg'] or i[
                        'rarity_value'] > max_item_rarity_to_donate or item_rank > max_item_rank_to_donate):
                        # TODO check if slots available for retrieving?
                        if isWeapon:
                            weapons_to_retrieve.append(i['id'])
                        else:
                            equipments_to_retrieve.append(i['id'])
                    else:
                        if isWeapon:
                            weapons_to_donate.append(i['id'])
                        else:
                            equipments_to_donate.append(i['id'])

            total_to_donate = len(weapons_to_donate) + len(equipments_to_donate)
            total_to_retrieve = len(weapons_to_retrieve) + len(equipments_to_retrieve)
            if finished_item_count > 0:
                self.log(
                    f"Finished leveling {finished_item_count} equipments - {total_to_retrieve} will be retrieved, {total_to_donate} will be donated")

            if total_to_retrieve > 0:
                result = self.client.breeding_center_pick_up(weapons_to_retrieve, equipments_to_retrieve)

                if (result['error'] == 'Maximum armour slot reached' or result[
                    'error'] == 'Maximum weapon slot reached'):
                    sell_equipments = result['error'] == 'Maximum armour slot reached'
                    sell_weapons = result['error'] == 'Maximum weapon slot reached'
                    self.shop_free_inventory_space(sell_weapons, sell_equipments, 20)
                    retry = True

            if total_to_donate > 0:
                result = self.kingdom_weapon_equipment_entry(weapons_to_donate, equipments_to_donate)

    # Will first try to fill the depository with items with rare innocents (any rank)
    # Rest of spots will be filled with any item of specified rank (r40 by default)
    def etna_resort_fill_depository(self, deposit_free_slots=0, max_innocent_rank=5, min_item_rank_to_deposit=40):
        if deposit_free_slots == 0:
            depository_data = self.client.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)

        if deposit_free_slots > 0:
            self.log(f"Filling depository with {deposit_free_slots} items...")
            # Fill depository with items that have rare innocents first, regrdless of item rank
            self.etna_resort_find_items_for_depository(deposit_free_slots, max_innocent_rank,
                                                       min_item_rank_to_deposit=0)

            # if slots available, fill with any item of specified rank
            depository_data = self.client.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)
            if deposit_free_slots > 0:
                self.etna_resort_find_items_for_depository(deposit_free_slots, 0, min_item_rank_to_deposit)

    # Look for items with specified criteria
    def etna_resort_find_items_for_depository(self, deposit_free_slots=0, max_innocent_rank=5,
                                              min_item_rank_to_deposit=40):
        if deposit_free_slots == 0:
            depository_data = self.client.breeding_center_list()
            items_in_depository = depository_data['result']['t_weapons'] + depository_data['result']['t_equipments']
            deposit_free_slots = 11 - len(items_in_depository)

        if deposit_free_slots > 0:
            self.player_weapons(True)
            self.player_equipment(True)
            weapons_to_deposit = []
            equipments_to_deposit = []
            weapons_lvl1 = [x for x in self.pd.weapons if x['lv'] <= 1 and x['set_chara_id'] == 0]
            equips_lvl1 = [x for x in self.pd.equipment if x['lv'] <= 1 and x['set_chara_id'] == 0]

            equipments_to_deposit = self.generate_array_for_deposit(equips_lvl1, deposit_free_slots, max_innocent_rank,
                                                                    min_item_rank_to_deposit)

            # If deposit cannot be filled with only equipment, find weapons to finish filling
            if len(equipments_to_deposit) < deposit_free_slots:
                deposit_free_slots = deposit_free_slots - len(equipments_to_deposit)
                weapons_to_deposit = self.generate_array_for_deposit(weapons_lvl1, deposit_free_slots,
                                                                     max_innocent_rank, min_item_rank_to_deposit)

            if len(weapons_to_deposit) > 0 or len(equipments_to_deposit) > 0:
                self.client.breeding_center_entrust(weapons_to_deposit, equipments_to_deposit)

    def generate_array_for_deposit(self, all_items, deposit_free_slots, max_innocent_rank, min_item_rank_to_deposit=40,
                                   max_rarity_to_deposit=40):
        deposit_count = 0
        items_to_deposit = []
        filled = False
        innocent_count = 0

        while not filled:
            # Looking for rare, iterate only once
            if max_innocent_rank > 0:
                filled = True

            for item in all_items:
                # If looking for rare innocents
                item_innocents = self.pd.get_item_innocents(item['id'])
                if max_innocent_rank > 0:
                    rare_innocents = [x for x in item_innocents if x['effect_rank'] >= max_innocent_rank]
                    if len(rare_innocents) > 0:
                        items_to_deposit.append(item['id'])
                        deposit_count += 1
                        if deposit_count == deposit_free_slots:
                            break

                            # Otherwise fill with commons of specific rank
                # fill with items with no innocents first, 
                # if there aren't enough iterate all items once again and find items with 1 inno
                else:
                    item_rank = self.gd.get_item_rank(item)
                    if item['rarity_value'] > max_rarity_to_deposit or item_rank < min_item_rank_to_deposit:
                        continue
                    if len(item_innocents) > innocent_count: continue
                    items_to_deposit.append(item['id'])
                    deposit_count += 1
                    if deposit_count == deposit_free_slots:
                        filled = True
                        break
            innocent_count += 1
        return items_to_deposit

    def etna_donate_innocents(self, max_innocent_rank=8, max_innocent_type=8):
        self.player_innocents()
        innos = []
        skipping = 0
        for i in self.pd.innocents:
            if not self._filter_innocent(i, max_innocent_rank, max_innocent_type):
                skipping += 1
                continue
            innos.append(i['id'])

        self.log('donate - skipping %s innocents' % skipping)
        if len(innos) > 0:
            for batch in (innos[i:i + 20] for i in range(0, len(innos), 20)):
                self.kingdom_innocent_entry(innocent_ids=batch)

    def etna_resort_donate_items(self, max_innocent_rank: int = 10, max_innocent_type: int = 8,
                                 max_item_rank: int = 100, max_item_rarity: int = 40):
        self.log("Looking for items to donate...")
        self.player_equipment(True)
        self.player_weapons(True)
        self.player_innocents(True)

        weapons_to_donate = []
        equipments_to_donate = []

        ec = 0
        wc = 0
        items, skipping = self.pd.filter_items(
            only_max_lvl=True, skip_locked=True,
            max_innocent_rank=max_innocent_rank,
            max_innocent_type=max_innocent_type,
            max_item_rank=max_item_rank,
            max_rarity=max_item_rarity
        )

        if len(items) > 0:
            for item in items:
                equip_type = self.pd.get_equip_type(item)
                self.remove_innocents(item)

                if equip_type == 2:
                    ec += 1
                    equipments_to_donate.append(item['id'])
                else:
                    wc += 1
                    weapons_to_donate.append(item['id'])
                self.log_donate(item)

        self.log(f"Will donate {wc} weapons and {ec} equipments")
        self.log('donate - skipping %s items' % skipping)

        for batch in (equipments_to_donate[i:i + 20] for i in range(0, len(equipments_to_donate), 20)):
            self.kingdom_weapon_equipment_entry(equipment_ids=batch)
        for batch in (weapons_to_donate[i:i + 20] for i in range(0, len(weapons_to_donate), 20)):
            self.kingdom_weapon_equipment_entry(weapon_ids=batch)

        self.log("Finished donating equipment")

    def etna_resort_refine_item(self, item_id):
        e = self.pd.get_weapon_by_id(item_id)
        if e is not None:
            item_type = 3
        else:
            item_type = 4
            e = self.pd.get_equipment_by_id(item_id)

        if e['rarity_value'] == 100:
            self.logger.warn("Item already has rarity 100...")
            return

        if e['lv'] != e['lv_max']:
            self.logger.warn("Item is not at max level...")
            return

        retry = True
        self.log("Attempting to refine item...")
        attempt_count = 0
        result = ''
        while retry:
            attempt_count += 1
            res = self.client.etna_resort_refine(item_type, item_id)
            if 'success_type' in res['result']:
                result = res['result']['success_type']
                retry = False
                if item_type == 3:
                    final_rarity = res['result']['t_weapon']['rarity_value']
                else:
                    final_rarity = res['result']['t_equipment']['rarity_value']
        self.log(
            f"Refined item. Attempts used {attempt_count}. Rarity increase: {result}. Current rarity {final_rarity}")

    def innocent_get_training_result(self, training_result):
        if training_result == Innocent_Training_Result.NORMAL:
            return "Normal"
        if training_result == Innocent_Training_Result.NOT_BAD:
            return "Not bad"
        if training_result == Innocent_Training_Result.DREAMLIKE:
            return "Dreamlike"

    def log_donate(self, w):
        item = self.gd.get_weapon(w['m_weapon_id']) if 'm_weapon_id' in w else self.gd.get_equipment(
            w['m_equipment_id'])
        self.logger.debug(
            '[-] donate item: "%s" rarity: %s rank: %s lv: %s lv_max: %s locked: %s' %
            (item['name'], w['rarity_value'], self.gd.get_item_rank(w), w['lv'],
             w['lv_max'], w['lock_flg'])
        )

    def _filter_innocent(self, i, max_innocent_rank, max_innocent_type):
        if i['place_id'] > 0:
            return False
        if i['effect_rank'] > max_innocent_rank:
            return False
        if i['innocent_type'] > max_innocent_type:
            return False
        return True
