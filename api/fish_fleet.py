import datetime
from abc import ABCMeta

from dateutil import parser

from api.constants import Fish_Fleet_Area_Bribe_Status, Fish_Fleet_Index, Fish_Fleet_Result_type
from api.player import Player


class FishFleet(Player, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    def survey_complete_all_expeditions_and_start_again(self, use_bribes, hours):
        serverDateTime = datetime.datetime.utcnow() + datetime.timedelta(hours=-4)
        fish_fleet_data = self.client.survey_index()
        for fish_fleet in fish_fleet_data['result']['t_surveys']:
            fleet_name = self.survey_get_fleet_name(fish_fleet['m_survey_id'])
            end_time_string = fish_fleet['end_at']
            ## fleet has been sent
            if fish_fleet['end_at'] != '':
                end_time_date_time = parser.parse(end_time_string)
                if serverDateTime > end_time_date_time:
                    # Complete expedition and print rewards
                    self.survey_complete_expedition(fish_fleet['m_survey_id'])
                    # Start expedition again
                    self.survey_start_expedition(fish_fleet['m_survey_id'], use_bribes, hours)
                else:
                    self.log(f"{fleet_name} fleet has not returned yet.")
            # Fleet not sent
            else:
                self.survey_start_expedition(fish_fleet['m_survey_id'], use_bribes, hours)

    def survey_complete_expedition(self, m_survey_id):
        fleet_name = self.survey_get_fleet_name(m_survey_id)
        end_data = self.client.survey_end(m_survey_id, False)
        self.log(
            f"{fleet_name} has returned - Result: {self.survey_get_result_type(end_data['result']['result_type'])}")
        self.log("Obtained the following rewards:")
        for drop in end_data['result']['drop_result']['drop_list']:
            # Item
            if drop['type'] == 1:
                item = self.gd.get_item(drop['id'])
                self.log(f"\tObtained {drop['num']} {item['name']}")
            # Character
            if drop['type'] == 2:
                unit_obtained = self.gd.get_character(drop['id'])
                self.log(f"\tObtained {drop['rarity']}★ character {unit_obtained['name']}")

    def survey_start_expedition(self, m_survey_id, use_bribes, hours):
        fish_fleet_data = self.client.survey_index()
        fish_fleet = [x for x in fish_fleet_data['result']['t_surveys'] if x['m_survey_id'] == m_survey_id][0]
        fleet_name = self.survey_get_fleet_name(m_survey_id)
        if fish_fleet['end_at'] == '':
            if use_bribes:
                self.log(f"Bribing {fleet_name} fleet expedition")
                bribe_status = fish_fleet['area_condition']
                # Bribe util max
                while bribe_status < Fish_Fleet_Area_Bribe_Status.VERY_MANY:
                    bribe_result = self.client.survey_use_bribe_item(m_survey_id, [{"m_item_id": 401, "num": 1}])
                    bribe_status = bribe_result['result']['t_survey']['area_condition']
            survey_start_data = self.client.survey_start(m_survey_id, hours, fish_fleet['t_character_ids'], [])
            self.log(f"Started {fleet_name} fleet expedition")

    def survey_get_fleet_name(self, m_survey_id):
        if m_survey_id == Fish_Fleet_Index.CHARACTER_EXP_FLEET:
            return "Character EXP Fleet"
        if m_survey_id == Fish_Fleet_Index.SKILL_EXP_FLEET:
            return "Skill EXP Fleet"
        if m_survey_id == Fish_Fleet_Index.WM_EXP_FLEET:
            return "WM EXP Fleet"

    def survey_get_result_type(self, result_type):
        if result_type == Fish_Fleet_Result_type.HARVEST_1:
            return "???"
        if result_type == Fish_Fleet_Result_type.NORMAL_HARVEST:
            return "Normal Harvest"
        if result_type == Fish_Fleet_Result_type.SUPER_HARVEST:
            return "Super Harvest"

    def survey_get_return_time(self):
        fish_fleet_data = self.client.survey_index()
        closest_fleet_end_time = datetime.datetime.max
        for fish_fleet in fish_fleet_data['result']['t_surveys']:
            end_time_string = fish_fleet['end_at']
            ## fleet has been sent
            if fish_fleet['end_at'] != '':
                end_time_date_time = parser.parse(end_time_string)
                if end_time_date_time < closest_fleet_end_time:
                    closest_fleet_end_time = end_time_date_time

        # No expedition has end date, return min date so they will be started
        if closest_fleet_end_time == datetime.datetime.max:
            closest_fleet_end_time = datetime.datetime.min

        return closest_fleet_end_time
