import os

from main import API

# ~beginnerfriendly bot.

# ~Remove the pound sign (#) Before a certain code Example: a.wait(1) to activate it. Don't remove #before #~explanations.
# ~Pound sign signals python to ignore text.

a = API()
a.sess = os.getenv('DRPG_TOKEN')    # ~Here you input your SESS code INSIDE the quotations.
a.uin = os.getenv('DRPG_UIN')       # ~Here you input your UIN code INSIDE the quotations.
a.setRegion(2)  # ~Sets your region as Global(2), Japan(1)
a.setDevice(2)  # ~Sets your device as Android(2), iOS(1)
a.dologin()
# This makes every action have SECONDS delay between them.
a.wait(1)


def farm_event(x):
    a.setTeamNum(9)
    for i in range(x):
        a.doQuest(1079105308)
    # exit(0)


def farm_gem_gates(team=1, start_at=10, human=True, monster=True):
    a.setTeamNum(team)
    if human:
        for stage in a.getAreaStages(50107):
            if stage['no'] > start_at:
                a.doQuest(stage['id'])
                a.doQuest(stage['id'])
                a.doQuest(stage['id'])
    if monster:
        for stage in a.getAreaStages(50108):
            if stage['no'] > start_at:
                a.doQuest(stage['id'])
                a.doQuest(stage['id'])
                a.doQuest(stage['id'])


def farm_item_world(team=1, min_rarity=40, min_item_rank=0, min_item_level=0):
    # Change the party: 1-9
    a.setTeamNum(team)
    # This changes the minimum rarity of equipments found in the item-world. 1 = common, 40 = rare, 70 = Legendary
    a.minrarity(min_rarity)

    # Only upgrade items that have this # of levels or greater
    a.minItemLevel(min_item_level)
    # Only upgrade items with the following rank
    a.minItemRank(min_item_rank)

    # This runs item-world to level all your items.
    a.upgradeItems()


# This runs all non cleared normal maps, and makes them 3 stars.
# a.completeStory(farmingAll=False)

# This will sell all non-equipped items that's below given rarity and rank.
a.sellItems(maxrarity=69, maxrank=30)
# farm_gem_gates(team=4)
farm_item_world(team=4, min_rarity=70, min_item_rank=39, min_item_level=0)

# a.doQuest(INPUT ID HERE)				#~This just runs given ID quest.
# a.completeStory(farmingAll=True)		#~This runs all normal maps, and makes them 3 stars.
# a.completeStory(farmingAll=False)		#~This runs all non cleared normal maps, and makes them 3 stars.
# a.completeStory(50101,farmingAll=True)	#~This runs all the EXP gates, and makes them 3 stars.
# a.completeStory(50102,farmingAll=True)	#~This runs all the HL gates, and makes them 3 stars.
# a.completeStory(50107,farmingAll=True)	#~This runs all the Gem Gates, humans. And makes them 3 stars.
# a.completeStory(50108,farmingAll=True)	#~This runs all the Gem Gates, monsters. And makes them 3 stars.
# a.boltrend_exchange_code('73rss7mw9i')	#~This will input gift codes. Copy paste the whole code for multiple gift codes.
