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
                #3 star finish
                #"common_battle_result":"eyJhbGciOiJIUzI1NiJ9.eyJoZmJtNzg0a2hrMjYzOXBmIjoiMSwxLDEiLCJ5cGIyODJ1dHR6ejc2Mnd4IjoyNTkxNjg1OTc1MjQsImRwcGNiZXc5bXo4Y3V3d24iOjAsInphY3N2NmpldjRpd3pqem0iOjAsImt5cXluaTNubm0zaTJhcWEiOjAsImVjaG02dGh0emNqNHl0eXQiOjAsImVrdXN2YXBncHBpazM1amoiOjAsInhhNWUzMjJtZ2VqNGY0eXEiOjR9.4NWzKTpAs-GrjbFt9M6eEJEbEviUf5xvrYPGiIL4V0k"
                # finish stage with steal 1k
                "common_battle_result":"eyJhbGciOiJIUzI1NiJ9.eyJoZmJtNzg0a2hrMjYzOXBmIjoiIiwieXBiMjgydXR0eno3NjJ3eCI6MjU0Mzc1NzMwOTcyLCJkcHBjYmV3OW16OGN1d3duIjowLCJ6YWNzdjZqZXY0aXd6anptIjowLCJreXF5bmkzbm5tM2kyYXFhIjowLCJlY2htNnRodHpjajR5dHl0IjowLCJla3VzdmFwZ3BwaWszNWpqIjoxMDEzLCJ4YTVlMzIybWdlajRmNHlxIjoxNn0.MWfmZHEHIVSFj-26a6bJ0tuMUGQP4496oA_Fxv8V8Tw"
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