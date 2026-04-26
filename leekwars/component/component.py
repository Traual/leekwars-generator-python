class Component:

    def __init__(self, id_, name, stats, template):
        self.id = id_
        self.name = name
        self.stats = {}
        for stat in stats:
            self.stats[stat[0]] = stat[1]
        self.template = template

    def getId(self) -> int:
        return self.id

    def getTemplate(self) -> int:
        return self.template

    def getStats(self):
        return self.stats

    def getName(self) -> str:
        return self.name
