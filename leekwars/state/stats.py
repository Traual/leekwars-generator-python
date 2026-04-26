class Stats:

    def __init__(self, other=None):
        if other is not None:
            self.stats = dict(other.stats)
        else:
            self.stats = {}

    def getStat(self, stat: int) -> int:
        retour = self.stats.get(stat)
        if retour is None:
            return 0
        return retour

    def addStats(self, to_add) -> None:
        for key, value in to_add.stats.items():
            self.updateStat(key, value)

    def setStat(self, key: int, value: int) -> None:
        self.stats[key] = value

    def clear(self) -> None:
        self.stats.clear()

    def updateStat(self, id_: int, delta: int) -> None:
        self.stats[id_] = self.stats.get(id_, 0) + delta
