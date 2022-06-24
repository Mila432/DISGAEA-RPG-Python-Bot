from main import API

a = API()
a.sess = ''
a.uin = ''
a.wait(0)
a.setRegion(2)
a.setDevice(2)
a.dologin()

#Set active party and print the IDs of the characters. Use them to run axel contest
a.setActiveParty(1)
print(a.deck)

unitID = 11111111
highestStageToClear = 50
number_of_characters = 10

# Specify single character to run
a.do_axel_contest(unitID, highestStageToClear)

# Bot will find any character to run through the Axel contest
a.do_axel_contest_multiple_characters(number_of_characters, highestStageToClear)