from abc import ABCMeta

from api.player import Player


class AxelContest(Player, metaclass=ABCMeta):

    def __init__(self):
        super().__init__()

    def find_character_for_axel_contest(self, highestStageToClear):
        # fetch all characters
        self.log("Looking for a character...")
        self.player_characters(True)
        # collections store axel contest progress.
        all_collections = self.player_character_collections()['result']['_items']
        collections_available = [x for x in all_collections if x['contest_stage'] < highestStageToClear]
        for collection in collections_available:
            # find the actual unit tht has the character_id
            character = self.pd.get_character_by_id(collection['m_character_id'])
            if character is not None:
                return character
        return None

    def get_battle_exp_data_axel_contest(self, start, unitID):
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
        if lastClearedStage < 49:
            return 1
        if lastClearedStage < 99:
            return 2
        if lastClearedStage < 199:
            return 3
        if lastClearedStage < 299:
            return 4
        if lastClearedStage < 399:
            return 5
        if lastClearedStage < 499:
            return 6
        if lastClearedStage < 599:
            return 7
        if lastClearedStage < 699:
            return 8
        if lastClearedStage < 799:
            return 9
        if lastClearedStage < 899:
            return 10
        if lastClearedStage < 999:
            return 12
        if lastClearedStage < 1099:
            return 14
        if lastClearedStage < 1199:
            return 16
        if lastClearedStage < 1299:
            return 18
        if lastClearedStage < 1399:
            return 20
        if lastClearedStage < 1499:
            return 24
        return 28

    def do_axel_contest_multiple_characters(self, numberOfCharacters, highestStageToClear):
        unit_count = 0
        while unit_count < numberOfCharacters:
            character = self.find_character_for_axel_contest(highestStageToClear)
            if character is None:
                self.log("No characters left, please increase the level cap")
                return
            self.do_axel_contest(character, highestStageToClear)
            unit_count += 1
            self.log(f"Completed {unit_count} out of {numberOfCharacters} characters")

    def do_axel_contest(self, character, highest_stage_to_clear):
        if isinstance(character, int):
            character = self.pd.get_character_by_id(character)
        cid = character['m_character_id']
        collection = self.pd.get_character_collection_by_mid(cid)

        if collection is None:
            self.log("Unit not found. Exiting...")
            return

        unit_name = self.gd.get_character(cid)['name']
        last_cleared_stage = collection['contest_stage'] if 'contest_stage' in collection else 0

        self.log(f"Started Axel Contest for {unit_name} - Last cleared stage: {last_cleared_stage}"
                 f" - Highest stage to clear {highest_stage_to_clear}")

        while last_cleared_stage < highest_stage_to_clear:
            act = self.get_axel_stage_energy_cost(last_cleared_stage)
            if act > self.current_ap:
                self.logger.warn('not enough ap')
                break

            start = self.client.axel_context_battle_start(
                act=act,
                m_character_id=collection['m_character_id'],
                t_character_ids=[character['id']]
            )
            self.check_resp(start)

            end = self.client.axel_context_battle_end(
                collection['m_character_id'],
                self.get_battle_exp_data_axel_contest(start, [cid]),
                "eyJhbGciOiJIUzI1NiJ9.eyJoZmJtNzg0a2hrMjYzOXBmIjoiIiwieXBiMjgydXR0eno3NjJ3eCI6ODY4MTY2ODE1OCwiZHBwY2JldzltejhjdXd3biI6MCwiemFjc3Y2amV2NGl3emp6bSI6NCwia3lxeW5pM25ubTNpMmFxYSI6MCwiZWNobTZ0aHR6Y2o0eXR5dCI6MCwiZWt1c3ZhcGdwcGlrMzVqaiI6MCwieGE1ZTMyMm1nZWo0ZjR5cSI6MH0.NudHEcTQfUUuOaNr9vsFiJkQwaw4nTL6yjK93jXzqLY")
            last_cleared_stage = end['result']['after_t_character_collections'][0]['contest_stage']
            self.log(f"Cleared stage {last_cleared_stage} of Axel Contest for {unit_name}.")

        self.log(f"Finished running Axel Contest for {unit_name} - Last cleared stage: {last_cleared_stage}")
