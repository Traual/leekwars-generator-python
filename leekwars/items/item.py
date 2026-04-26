class Item:

    def __init__(self, id, cost, name, template, attack):
        self.id = id
        self.cost = cost
        self.name = name
        self.template = template
        self.attack = attack

    def getTemplate(self) -> int:
        return self.template

    def getId(self) -> int:
        return self.id

    def getCost(self) -> int:
        return self.cost

    def getAttack(self):
        return self.attack

    def getName(self) -> str:
        return self.name
