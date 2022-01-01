from api import Player


class Gatcha(Player):
    def __init__(self):
        super().__init__()

    def gacha_available(self):
        data = self.rpc('gacha/available', {})
        return data

    def gacha_do(self, is_gacha_free, price, item_type, num, m_gacha_id, item_id):
        data = self.rpc('gacha/do', {"is_gacha_free": is_gacha_free, "price": price, "item_type": item_type, "num": num,
                                     "m_gacha_id": m_gacha_id, "item_id": item_id})
        return data

    def gacha_sums(self):
        data = self.rpc('gacha/sums', {})
        return data

    def getfreegacha(self):
        res = self.gacha_available()
        if len(res['result']['private_gachas']) > 0:
            self.gacha_do(is_gacha_free=True, price=0, item_type=2, num=1, m_gacha_id=100001, item_id=0)
