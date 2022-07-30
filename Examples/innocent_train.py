from api.constants import Constants, Innocent_ID
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

# Get all innocents from a specific type that are not part of any equipment
# Upgrade innocents that are one step away from legendary
# Use for HP, RES, DEF so you can donate them in bulk

inital_innocent_rank = 8
max_innocent_rank = 9
all_available_innocents = a.pd.innocent_get_all_of_type(Innocent_ID.HP, only_unequipped=True)
innocents_trained = 0
tickets_finished = False

for innocent in all_available_innocents:

    if tickets_finished:
        break

    effect_rank = innocent['effect_rank']
    if effect_rank < inital_innocent_rank or effect_rank >= max_innocent_rank:
        continue
    print(f"\nFound innocent to train. Starting value: {innocent['effect_values'][0]}")
    attempts = 0
    innocents_trained += 1
    while effect_rank < max_innocent_rank:
        res = a.client.innocent_training(innocent['id'])
        if ('api_error' in res and 'message' in res['api_error'] and res['api_error']['message'] == 'Not enough item.'):
            print("No caretaker tickets left")
            tickets_finished = True
            break
        effect_rank = res['result']['after_t_data']['innocents'][0]['effect_rank']
        print(
            f"\tTrained innocent with result {a.innocent_get_training_result(res['result']['training_result'])} - Current value: {res['result']['after_t_data']['innocents'][0]['effect_values'][0]}")
        attempts += 1
    print(f"\tUpgraded innocent to Legendary. Finished training. Total attempts: {attempts}")
print(f"\nNo innocents left to train. Total innocents trained: {innocents_trained}")
