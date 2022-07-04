from abc import ABCMeta
from data import data as gamedata

class AxelContest(metaclass=ABCMeta):
    
    def __init__(self):
        super().__init__()

    def find_character_for_axel_contest(self, highestStageToClear):
        # fetch all characters
        print("Looking for a character...")
        self.player_characters_get_all()   
        #collections store axel contest progress.     
        allCollections = self.player_character_collections()['result']['_items']
        collections_available = [x for x in allCollections if x['contest_stage'] < highestStageToClear]
        for collection in collections_available:          
            #find the actual unit tht has the character_id
            character = self.find_character_by_characterid(collection['m_character_id'])
            if character is not None:
                return character
        return None

    def axel_context_battle_start(self, act, m_character_id, t_character_ids):
        data = self.rpc('character_contest/start', 
            {"act":act,"m_character_id":m_character_id,"t_character_ids":t_character_ids})
        return data

    def axel_context_battle_end(self, m_character_id,                   
                              battle_exp_data,                              
                              common_battle_result):
        data = self.rpc(
            'battle/end', {
                "m_stage_id": 0,
                "m_tower_no": 0,
                "equipment_id": 0,
                "equipment_type": 0,
                "innocent_dead_flg": 0,
                "t_raid_status_id": 0,
                "raid_battle_result": "", 
                "m_character_id": m_character_id,
                "division_battle_result": "",
                "battle_type": 7,
                "result": 1,
                "battle_exp_data": battle_exp_data,
                "common_battle_result":common_battle_result,
                "skip_party_update_flg": True                
            })
        return data

    def getbattle_exp_data_axel_contest(self, start, unitID):
        res = []
        for d in start['result']['enemy_list']:
            for r in d:
                res.append({
                    "finish_member_ids": unitID,
                    "finish_type": 1,
                    "m_enemy_id": d[r]
                })
        return res

    def get_axel_stage_energy_cost(self, lastClearedStage):
        if(lastClearedStage < 49):
            return 1
        if(lastClearedStage < 99):
            return 2
        if(lastClearedStage < 199):
            return 3
        if(lastClearedStage < 299):
            return 4
        if(lastClearedStage < 399):
            return 5
        if(lastClearedStage < 499):
            return 6
        if(lastClearedStage < 599):
            return 7
        if(lastClearedStage < 699):
            return 8
        if(lastClearedStage < 799):
            return 9
        if(lastClearedStage < 899):
            return 10
        if(lastClearedStage < 999):
            return 12
        if(lastClearedStage < 1099):
            return 14
        if(lastClearedStage < 1199):
            return 16
        if(lastClearedStage < 1299):
            return 18
        if(lastClearedStage < 1399):
            return 20
        if(lastClearedStage < 1499):
            return 24
        return 28

    def do_axel_contest_multiple_characters(self, numberOfCharacters, highestStageToClear):        
        unitCount = 0
        while unitCount < numberOfCharacters:
            character = self.find_character_for_axel_contest(highestStageToClear)
            if(character is None):
                print("No characters left, please increase the level cap")
                return
            self.do_axel_contest(character, highestStageToClear)
            unitCount+=1
            print(f"Completed {unitCount} out of {numberOfCharacters} characters")

    def do_axel_contest(self, character, highestStageToClear):
        if not isinstance(character, int):            
            character = character['id']
                    
        collection = self.find_character_collection_by_character_id(character)
        if collection is None: 
            print("Unit not found. Exiting...")
            return
    
        unitName = self.getChar(collection['m_character_id'])['name']
        lastClearedStage = collection['contest_stage']
        print(f"Started Axel Contest for {unitName} - Last cleared stage: {lastClearedStage} - Highest stage to clear {highestStageToClear}")

        while lastClearedStage < highestStageToClear:
            start = self.axel_context_battle_start(self.get_axel_stage_energy_cost(lastClearedStage), collection['m_character_id'], [character])
            end = self.axel_context_battle_end(                             
                              collection['m_character_id'],
                              self.getbattle_exp_data_axel_contest(start, [character]),
                              "eyJhbGciOiJIUzI1NiJ9.eyJoZmJtNzg0a2hrMjYzOXBmIjoiIiwieXBiMjgydXR0eno3NjJ3eCI6ODY4MTY2ODE1OCwiZHBwY2JldzltejhjdXd3biI6MCwiemFjc3Y2amV2NGl3emp6bSI6NCwia3lxeW5pM25ubTNpMmFxYSI6MCwiZWNobTZ0aHR6Y2o0eXR5dCI6MCwiZWt1c3ZhcGdwcGlrMzVqaiI6MCwieGE1ZTMyMm1nZWo0ZjR5cSI6MH0.NudHEcTQfUUuOaNr9vsFiJkQwaw4nTL6yjK93jXzqLY")
            lastClearedStage = end['result']['after_t_character_collections'][0]['contest_stage']
            print(f"Cleared stage {lastClearedStage} of Axel Contest for {unitName}.")

        print(f"Finished running Axel Contest for {unitName} - Last cleared stage: {lastClearedStage}")