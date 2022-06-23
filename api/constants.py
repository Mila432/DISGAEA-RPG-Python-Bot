from enum import Enum, IntEnum

class Constants:
    Current_Raid_ID = 135
    Current_Raid_Event_Point_Gacha = 49
    Current_Raid_Innocent_Regular_Roulette = 49
    Current_Raid_Innocent_Special_Roulette = 49
    Current_Raid_Regular_Boss_Stage = "vs. Swimsuit Prinny"
    Current_Raid_Badass_Boss_Stage = "vs. Swimsuit Prinny Badass"
    Current_Bingo_ID = 2

class Bingo_ID(IntEnum):
    JUNE_2022 = 2
    JULY_2022 = 0

class Raid_Gacha_ID(IntEnum):
    SUMMER_PRINNY_EVENT_POINT = 49
    SUMMER_PRINNY_INNOCENT_REGULAR_ROULETTE = 50
    SUMMER_PRINNY_INNOCENT_SPECIAL_ROULETTE = 51

class Raid_ID(IntEnum):
    SUMMER_PRINNY_RAID_ID = 135
    MAKAI_KINGDOM_RAID_ID = 0
    KAGEMARU_RAID_ID = 0

class Raid_Boss_Stage_Names(str, Enum):
    SUMMER_PRINNY_REGULAR_BOSS = "vs. Swimsuit Prinny"
    SUMMER_PRINNY_BADASS_BOSS = "vs. Swimsuit Prinny Badass"
    MAKAI_KINGDOM_REGULAR_BOSS = "vs. Dark Lord Valvoga"
    MAKAI_KINGDOM_BADASS_BOSS = "vs. Dark Lord Valvoga Badass"
    SEVENDEADLYSINS_REGULAR_BOSS = "vs. Diane"
    SEVENDEADLYSINS_BADASS_BOSS = "vs. Diane Badass"
    KAGEMARU_REGULAR_BOSS = "vs. Kagemaru"
    KAGEMARU_BADASS_BOSS = "vs. Kagemaru Badass"