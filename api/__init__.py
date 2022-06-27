from abc import ABC
from api.raid import Raid
from api.axel_contest import AxelContest
from api.fish_fleet import FishFleet
from api.shop import Shop
from api.bingo import Bingo
from api.battle import Battle

class BaseAPI(Raid, AxelContest, FishFleet, Shop, Bingo, Battle, ABC):
    def __init__(self):
        super().__init__()