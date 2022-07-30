from api.constants import Constants
from main import API

a = API()
a.config(
    sess=Constants.session_id,
    uin=Constants.user_id,
    wait=0,
    region=2,
    device=2
)
a.dologin()

# a.setActiveParty(5)
# a.minrarity(95)
max_innocent_rank = 5  # do not donate items with innocents above this rank
max_item_rarity = 40  # do not donate items above this rarity
max_item_rank = 40  # do not donate items above this rank
min_item_rank_to_run = 40  # do not run IW for items below this rank
batch_size = 15
batches_to_run = 3

# a.sell_r40_equipment_with_no_innocents()

# Will run through X items in a batch
# After each batch will donate items and sell items that have no innocents to open up inventory space
# Keep runLimit=1 so that it check the depository after each item completed
batch_count = 0
while batch_count < batches_to_run:
    item_count = 0
    while item_count < batch_size:
        a.upgrade_items(ensure_drops=True, only_weapons=False, run_limit=1)
        a.etna_resort_check_deposit_status(max_innocent_rank, max_item_rank, max_item_rarity)
        item_count += 1
    a.etna_resort_donate_items(max_innocent_rank, max_item_rank, max_item_rarity)
    a.sell_r40_equipment_with_no_innocents()
    batch_count += 1

# a.lock_equipment_with_rare_innocents()
# a.lock_equipment_with_rare_innocents(max_innocent_rank=5, max_item_rarity = 70, max_item_rank=40)
