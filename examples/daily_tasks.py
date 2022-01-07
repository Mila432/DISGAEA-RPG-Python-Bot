import os

from main import API

a = API()
a.sess = os.getenv('DRPG_TOKEN')  # ~Here you input your SESS code INSIDE the quotations.
a.uin = os.getenv('DRPG_UIN')  # ~Here you input your UIN code INSIDE the quotations.
a.setRegion(2)  # ~Sets your region as Global(2), Japan(1)
a.setDevice(2)  # ~Sets your device as Android(2), iOS(1)
a.dologin()
# This makes every action have SECONDS delay between them.
a.wait(1)


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


def farm_hl_gates(team=1, start_at=10):
    a.setTeamNum(team)
    for stage in a.getAreaStages(50102):
        if stage['no'] > start_at:
            a.doQuest(stage['id'])
            a.doQuest(stage['id'])
            a.doQuest(stage['id'])


a.get_mail_and_rewards()
farm_gem_gates(team=7)
farm_hl_gates(team=8)
