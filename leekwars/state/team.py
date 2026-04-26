class Team:

    def __init__(self, other=None, state=None):
        if other is not None and state is not None:
            self.entities = []
            for entity in other.entities:
                self.entities.append(state.getEntity(entity.getFId()))
            self.cooldowns = dict(other.cooldowns)
            self.flags = set(other.flags)
            self.id = other.id
        else:
            self.entities = []
            self.cooldowns = {}
            self.flags = set()
            self.id = 0

    def getCooldowns(self):
        return self.cooldowns

    def getEntities(self):
        return self.entities

    def getFlags(self):
        return self.flags

    def addFlag(self, flag: int) -> None:
        self.flags.add(flag)

    def setID(self, id_: int) -> None:
        self.id = id_

    def getID(self) -> int:
        return self.id

    def addEntity(self, entity) -> None:
        self.entities.append(entity)

    def removeEntity(self, invoc) -> None:
        if invoc in self.entities:
            self.entities.remove(invoc)

    def isDead(self) -> bool:
        from .entity import Entity
        for entity in self.entities:
            # The team is dead if the turret is dead
            if entity.getType() == Entity.TYPE_TURRET and entity.isDead():
                return True
        for entity in self.entities:
            # The team is not dead if there is an alive leek
            if entity.getType() != Entity.TYPE_TURRET and not entity.isDead():
                return False
        return True

    def isAlive(self) -> bool:
        return not self.isDead()

    def size(self) -> int:
        return len(self.entities)

    def addCooldown(self, chip, cooldown: int) -> None:
        from .state import State
        self.cooldowns[chip.getId()] = State.MAX_TURNS + 2 if cooldown == -1 else cooldown

    def hasCooldown(self, chipID: int) -> bool:
        return chipID in self.cooldowns

    def getCooldown(self, chipID: int) -> int:
        if not self.hasCooldown(chipID):
            return 0
        return self.cooldowns[chipID]

    def applyCoolDown(self) -> None:
        cooldown_copy = dict(self.cooldowns)
        for chipID, value in cooldown_copy.items():
            if value <= 1:
                del self.cooldowns[chipID]
            else:
                self.cooldowns[chipID] = value - 1

    def getSummonCount(self) -> int:
        nb = 0
        for e in self.entities:
            if not e.isDead() and e.isSummon():
                nb += 1
        return nb

    def getDeadRatio(self) -> float:
        dead = 0
        total = 0
        for entity in self.entities:
            if entity.isSummon():
                continue
            total += 1
            if entity.isDead():
                dead += 1
        return dead / total if total > 0 else 0

    def getLifeRatio(self) -> float:
        from ..turret.turret import Turret
        life = 0
        total = 0
        for entity in self.entities:
            if entity.isSummon():
                continue
            if isinstance(entity, Turret):
                continue
            total += entity.getTotalLife()
            life += entity.getLife()
        return life / total if total > 0 else 0

    def containsChest(self) -> bool:
        from .entity import Entity
        for entity in self.entities:
            if entity.getType() == Entity.TYPE_CHEST:
                return True
        return False

    def getLife(self) -> int:
        from ..turret.turret import Turret
        life = 0
        for entity in self.entities:
            if entity.isSummon():
                continue
            if isinstance(entity, Turret):
                continue
            life += entity.getLife()
        return life
