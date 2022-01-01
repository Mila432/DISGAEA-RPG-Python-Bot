from abc import ABC

from api.base import Base
from api.player import Player
from api.gatcha import Gatcha
from api.battle import Battle
from api.shop import Shop


class BaseAPI(Shop, Gatcha, Battle, ABC):
    def __init__(self):
        super().__init__()
