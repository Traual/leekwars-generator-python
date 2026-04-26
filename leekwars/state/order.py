class Order:

    def __init__(self, other=None, state=None):
        if other is not None and state is not None:
            self.leeks = []
            self.position = other.position
            self.turn = other.turn
            for entity in other.leeks:
                self.leeks.append(state.getEntity(entity.getFId()))
        else:
            self.leeks = []
            self.position = 0
            self.turn = 1

    def addEntity(self, *args):
        if len(args) == 1:
            leek = args[0]
            self.leeks.append(leek)
        else:
            index, invoc = args
            self.leeks.insert(index, invoc)
            if index <= self.position:
                self.position += 1

    def addSummon(self, owner, invoc) -> None:
        if owner not in self.leeks:
            return
        self.leeks.insert(self.leeks.index(owner) + 1, invoc)

    def removeEntity(self, leek) -> None:
        try:
            index = self.leeks.index(leek)
        except ValueError:
            return
        if index <= self.position:
            self.position -= 1
        self.leeks.pop(index)
        if self.position == -1:
            self.position = len(self.leeks) - 1
            self.turn -= 1

    def current(self):
        if self.position < 0 or len(self.leeks) <= self.position:
            return None
        return self.leeks[self.position]

    def getTurn(self) -> int:
        return self.turn

    def getEntityTurnOrder(self, e) -> int:
        try:
            return self.leeks.index(e) + 1
        except ValueError:
            return 0

    def next(self) -> bool:
        self.position += 1
        if self.position >= len(self.leeks):
            self.turn += 1
            self.position = self.position % len(self.leeks)
            return True
        return False

    def getNextPlayer(self, entity=None):
        if entity is None:
            return self.leeks[(self.position + 1) % len(self.leeks)]
        try:
            index = self.leeks.index(entity)
        except ValueError:
            return None
        return self.leeks[(index + 1) % len(self.leeks)]

    def getPreviousPlayer(self, entity=None):
        if entity is None:
            p = self.position - 1
            if p < 0:
                p += len(self.leeks)
            return self.leeks[p]
        try:
            index = self.leeks.index(entity)
        except ValueError:
            return None
        p = index - 1
        if p < 0:
            p += len(self.leeks)
        return self.leeks[p]

    def getEntities(self):
        return self.leeks

    def getPosition(self) -> int:
        return self.position
