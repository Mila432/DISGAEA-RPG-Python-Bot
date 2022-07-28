from abc import ABCMeta
import time

class Battle(metaclass=ABCMeta):
    
    def __init__(self):
        super().__init__()

    def battle_help_list(self):
        data = self.rpc('battle/help_list', {})
        return data

    def battle_help_get_friend_by_id(self, help_t_player_id):
        friend = None
        print("Looking for friend")
        while friend == None:
            help_players = self.battle_help_list()['result']['help_players']
            friend = next((x for x in help_players if x['t_player_id'] == help_t_player_id), None) 
            time.sleep(1)
        return friend

    def battle_start(self, m_stage_id, help_t_player_id, help_t_character_id,
                     act, help_t_character_lv):
        data = self.rpc(
            'battle/start', {
                "t_character_ids": [],
                "t_deck_no": self.activeParty,
                "m_stage_id": m_stage_id,
                "m_guest_character_id": 0,
                "help_t_player_id": help_t_player_id,
                "t_raid_status_id": 0,
                "help_t_character_id": help_t_character_id,
                "auto_rebirth_t_character_ids": self.reincarnationIDs,
                "act": act,
                "help_t_character_lv": help_t_character_lv
            })
        return data

    def battle_skip(self, m_stage_id, skip_number, help_t_player_id = 0):

        if(help_t_player_id == 0):
            helper_player = self.battle_help_list()['result']['help_players'][0] 
        else:
            helper_player = self.battle_help_get_friend_by_id(help_t_player_id) 

        stage = self.getStage(m_stage_id)
        data = self.rpc(
            'battle/skip', 
            {
                "m_stage_id":m_stage_id,
                "help_t_player_id":helper_player['t_player_id'],
                "help_t_character_id":helper_player['t_character']['id'],
                "help_t_character_lv":helper_player['t_character']['lv'],
                "t_deck_no":self.activeParty,
                "m_guest_character_id":0,
                "t_character_ids":[],
                "skip_num":skip_number,
                "battle_type":3, # needs to be tested. It was an exp gate
                "act":stage['act'] * skip_number,
                "auto_rebirth_t_character_ids":self.reincarnationIDs,
                "t_memery_ids":[] #pass parameters?
            })
        return data

    # m_stage_ids [5010711,5010712,5010713,5010714,5010715] for monster reincarnation
    def battle_skip_stages(self, m_stage_ids, help_t_player_id = 0):

        if(help_t_player_id == 0):
            helper_player = self.battle_help_list()['result']['help_players'][0] 
        else:
            helper_player = self.battle_help_get_friend_by_id(help_t_player_id) 

        # calculate ap usage. Every stage is skipped 3 times
        act = 0
        for m_stage_id in m_stage_ids:
            stage = self.getStage(m_stage_id)
            act = act + (stage['act'] * 3)

        data = self.rpc(
            'battle/skip_stages', 
            {
                "m_stage_id":0,
                "help_t_player_id":helper_player['t_player_id'],
                "help_t_character_id":helper_player['t_character']['id'],
                "help_t_character_lv":helper_player['t_character']['lv'],
                "t_deck_no":self.activeParty,
                "m_guest_character_id":0,
                "t_character_ids":[],
                "skip_num":0,
                "battle_type":3, # needs to be tested. It was an exp gate
                "act":act,
                "auto_rebirth_t_character_ids":self.reincarnationIDs,
                "t_memery_ids":[], #pass parameters?
                "m_stage_ids":m_stage_ids
            })
        return data

    def battle_end(self, battle_exp_data, m_stage_id, battle_type,
                   result, equipment_id=0, equipment_type=0, m_tower_no=0):
        data = self.rpc(
            'battle/end', {
                "battle_exp_data": battle_exp_data,
                "equipment_type": equipment_type,
                "m_tower_no": m_tower_no,
                "raid_battle_result": "",
                "m_stage_id": m_stage_id,
                "equipment_id": equipment_id,
                "t_raid_status_id": 0,
                "battle_type": battle_type,
                "result": result,
                "innocent_dead_flg": 0,
                "skip_party_update_flg":True,
                #3 star finish
                "common_battle_result":"eyJhbGciOiJIUzI1NiJ9.eyJoZmJtNzg0a2hrMjYzOXBmIjoiMSwxLDEiLCJ5cGIyODJ1dHR6ejc2Mnd4IjoyNTkxNjg1OTc1MjQsImRwcGNiZXc5bXo4Y3V3d24iOjAsInphY3N2NmpldjRpd3pqem0iOjAsImt5cXluaTNubm0zaTJhcWEiOjAsImVjaG02dGh0emNqNHl0eXQiOjAsImVrdXN2YXBncHBpazM1amoiOjAsInhhNWUzMjJtZ2VqNGY0eXEiOjR9.4NWzKTpAs-GrjbFt9M6eEJEbEviUf5xvrYPGiIL4V0k"
                })
        return data

    def battle_story(self, m_stage_id):
        data = self.rpc('battle/story', {"m_stage_id": m_stage_id})
        return data

    def tower_start(self, m_tower_no):
        data = self.rpc('tower/start', {
            "t_deck_no": self.activeParty,
            "m_tower_no": m_tower_no
        })
        return data

    def doTower(self, m_tower_no=1):
        start = self.tower_start(m_tower_no)
        end = self.battle_end(battle_exp_data=self.getbattle_exp_data(start),
                              m_tower_no=m_tower_no,
                              m_stage_id=0,
                              battle_type=4,
                              result=1)
        return end

    def battle_skip_parties(self):
        data = self.rpc('battle/skip_parties', {})
        return data