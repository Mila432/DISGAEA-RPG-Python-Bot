import os

from main import API

a = API()
a.config(
    sess=os.getenv('DRPG_TOKEN'),
    uin=os.getenv('DRPG_UIN'),
    wait=0,
    region=2,
    device=2
)
a.quick_login()

# Set active party and print the IDs of the characters. Use them to run axel contest
a.options.team_num = 1
print(a.pd.deck)
exit(0)

unitID = 11111111
highestStageToClear = 50
number_of_characters = 10

# Specify single character to run
a.do_axel_contest(unitID, highestStageToClear)

# Bot will find any character to run through the Axel contest
a.do_axel_contest_multiple_characters(number_of_characters, highestStageToClear)
