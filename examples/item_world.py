import os

from main import API

# ~beginnerfriendly bot.

# ~Remove the pound sign (#) Before a certain code Example: a.wait(1) to activate it. Don't remove #before #~explanations.
# ~Pound sign signals python to ignore text.

a = API()
a.sess = os.getenv('DRPG_TOKEN')  # ~Here you input your SESS code INSIDE the quotations.
a.uin = os.getenv('DRPG_UIN')  # ~Here you input your UIN code INSIDE the quotations.
a.setRegion(2)  # ~Sets your region as Global(2), Japan(1)
a.setDevice(2)  # ~Sets your device as Android(2), iOS(1)
a.dologin()
# This makes every action have SECONDS delay between them.
a.wait(1)


def farm_item_world(team=1, min_rarity=40, min_rank=0, min_item_rank=0, min_item_level=0, only_weapons=False):
    a.onlyWeapons(only_weapons)
    # Change the party: 1-9
    a.setTeamNum(team)
    # This changes the minimum rarity of equipments found in the item-world. 1 = common, 40 = rare, 70 = Legendary
    a.minrarity(min_rarity)
    # This changes the min rank of equipments found in the item-world
    a.minrank(min_rank)
    # Only upgrade items that have this # of levels or greater
    a.minItemLevel(min_item_level)
    # Only upgrade items with the following rank
    a.minItemRank(min_item_rank)
    # This runs item-world to level all your items.
    a.upgradeItems()


a.get_mail_and_rewards()
# Will enable auto reincarnation
a.autoRebirth(True)
# This will sell all non-equipped items that's below given rarity and rank.
a.sellItems(maxrarity=39, maxrank=39, keep_max_lvl=True)
farm_item_world(team=2, min_rarity=70, min_rank=40, min_item_rank=40, min_item_level=0, only_weapons=False)
