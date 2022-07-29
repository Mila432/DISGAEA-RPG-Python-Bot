from abc import ABC

from api.base import Base
from api.player import Player
from api.gatcha import Gatcha
from api.battle import Battle
from api.shop import Shop
from api.items import Items
from api.axel_contest import AxelContest
from api.bingo import Bingo
from api.raid import Raid
from api.axel_contest import AxelContest
from api.fish_fleet import FishFleet
from api.shop import Shop
from api.bingo import Bingo
from api.battle import Battle
from api.etna_resort import EtnaResort
from api.items import Items


class BaseAPI(Bingo, Raid, AxelContest, FishFleet, Gatcha, Battle, EtnaResort, ABC):
    def __init__(self):
        super().__init__()
