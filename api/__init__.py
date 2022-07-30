from abc import ABC

from api.axel_contest import AxelContest
from api.axel_contest import AxelContest
from api.base import Base
from api.battle import Battle
from api.battle import Battle
from api.bingo import Bingo
from api.bingo import Bingo
from api.etna_resort import EtnaResort
from api.fish_fleet import FishFleet
from api.gatcha import Gatcha
from api.items import Items
from api.items import Items
from api.player import Player
from api.raid import Raid
from api.shop import Shop
from api.shop import Shop


class BaseAPI(Bingo, Raid, AxelContest, FishFleet, Gatcha, Battle, EtnaResort, ABC):
    def __init__(self):
        super().__init__()
