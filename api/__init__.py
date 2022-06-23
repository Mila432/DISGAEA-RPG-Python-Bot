from abc import ABC

#from api.base import Base
from api.raid import Raid
from api.axel_contest import AxelContest
#from api.gatcha import Gatcha
#from api.battle import Battle
#from api.shop import Shop
#from api.items import Items


class BaseAPI(Raid, AxelContest, ABC):
    def __init__(self):
        super().__init__()