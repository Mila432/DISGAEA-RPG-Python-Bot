from enum import Enum, IntEnum


class Constants:
    Current_Raid_ID = 143
    Current_Raid_Event_Point_Gacha = 52
    Current_Raid_Innocent_Regular_Roulette = 53
    Current_Raid_Innocent_Special_Roulette = 54
    Current_Raid_Regular_Boss_Stage = "vs. Dark Lord Valvoga"
    Current_Raid_Badass_Boss_Stage = "vs. Dark Lord Valvoga Badass"
    Current_Raid_Normal_Boss_ID = 1431
    Current_Raid_Badass_Boss_ID = 1432
    Current_Bingo_ID = 2
    session_id = ''  # FILL SESSION_ID HERE
    user_id = ''  # FILL USER_ID HERE
    ticket = ''  # FILL TICKET FOR STEAM LOGIN


class Raid_Gacha_ID(IntEnum):
    SUMMER_PRINNY_EVENT_POINT = 49
    SUMMER_PRINNY_INNOCENT_REGULAR_ROULETTE = 50
    SUMMER_PRINNY_INNOCENT_SPECIAL_ROULETTE = 51
    MAKAI_KINGDOM_EVENT_POINT = 52
    MAKAI_KINGDOM_INNOCENT_REGULAR_ROULETTE = 53
    MAKAI_KINGDOM_INNOCENT_SPECIAL_ROULETTE = 54


class Raid_ID(IntEnum):
    SUMMER_PRINNY_RAID_ID = 135
    MAKAI_KINGDOM_RAID_ID = 143
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


class Fish_Fleet_Index(IntEnum):
    CHARACTER_EXP_FLEET = 1
    SKILL_EXP_FLEET = 2
    WM_EXP_FLEET = 3


class Fish_Fleet_Result_type(IntEnum):
    HARVEST_1 = 1
    NORMAL_HARVEST = 2
    SUPER_HARVEST = 3


class Fish_Fleet_Survey_Duration(IntEnum):
    HOURS_6 = 6
    HOURS_12 = 12
    HOURS_18 = 18
    HOURS_24 = 24


class Fish_Fleet_Area_Bribe_Status(IntEnum):
    VERY_FEW = 1
    FEW = 2
    COMMON = 3
    MANY = 4
    VERY_MANY = 5


class Innocent_Status(IntEnum):
    NOT_SUBDUED = 0
    SUBDUED = 1
    ESCAPED = 2


class Innocent_Training_Result(IntEnum):
    NORMAL = 1
    NOT_BAD = 2
    DREAMLIKE = 3


# There's innocent type and innocent id. The Glasses INT inno has the same type as the regular INT inno, but different ID
class Innocent_ID(IntEnum):
    HP = 1
    ATK = 2
    DEF = 3
    INT = 4
    RES = 5
    SPD = 6
    EXP = 7
    HL = 8
