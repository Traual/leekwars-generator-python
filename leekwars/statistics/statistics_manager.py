from abc import ABC, abstractmethod


class StatisticsManager(ABC):
    """Statistics interface matching the Java statistics manager."""

    @abstractmethod
    def init(self, entity): pass

    @abstractmethod
    def say(self, entity, message): pass

    @abstractmethod
    def teleportation(self, entity, caster, start, end, itemId): pass

    @abstractmethod
    def lama(self, entity): pass

    @abstractmethod
    def characteristics(self, entity): pass

    @abstractmethod
    def updateStat(self, entity, characteristic, delta, caster): pass

    @abstractmethod
    def tooMuchOperations(self, entity): pass

    @abstractmethod
    def stackOverflow(self, entity): pass

    @abstractmethod
    def damage(self, entity, attacker, damage, direct, effect): pass

    @abstractmethod
    def summon(self, entity, summon): pass

    @abstractmethod
    def useTP(self, tp): pass

    @abstractmethod
    def heal(self, healer, entity, pv): pass

    @abstractmethod
    def error(self, entity): pass

    @abstractmethod
    def useChip(self, caster, chip, cell, targets, cellEntity): pass

    @abstractmethod
    def useWeapon(self, caster, weapon, cell, targets, cellEntity): pass

    @abstractmethod
    def kill(self, killer, entity, item, killCell): pass

    @abstractmethod
    def critical(self, launcher): pass

    @abstractmethod
    def endFight(self, values): pass

    @abstractmethod
    def addTimes(self, current, time_, operations): pass

    @abstractmethod
    def move(self, mover, entity, start, path): pass

    @abstractmethod
    def resurrect(self, caster, target): pass

    @abstractmethod
    def getOperationsByEntity(self): pass

    @abstractmethod
    def tooMuchDebug(self, farmer): pass

    @abstractmethod
    def show(self, mEntity, cell_id): pass

    @abstractmethod
    def slide(self, entity, caster, start, cell): pass

    @abstractmethod
    def useInvalidPosition(self, caster, attack, target): pass

    @abstractmethod
    def effect(self, entity, caster, effect): pass

    @abstractmethod
    def entityTurn(self, entity): pass

    @abstractmethod
    def antidote(self, entity, caster, poisonsRemoved): pass

    @abstractmethod
    def vitality(self, entity, caster, vitality): pass

    @abstractmethod
    def registerWrite(self, entity, key, value): pass

    @abstractmethod
    def setWeapon(self, entity, w): pass

    @abstractmethod
    def chest(self): pass

    @abstractmethod
    def chestKilled(self, killer, entity, resources): pass


class DefaultStatisticsManager(StatisticsManager):
    """No-op statistics manager. Useful when statistics aren't needed."""

    def __init__(self):
        self._opsByEntity = {}
        self._fight = None

    def setGeneratorFight(self, fight): self._fight = fight
    def init(self, entity): pass
    def say(self, entity, message): pass
    def teleportation(self, entity, caster, start, end, itemId): pass
    def lama(self, entity): pass
    def characteristics(self, entity): pass
    def updateStat(self, entity, characteristic, delta, caster): pass
    def tooMuchOperations(self, entity): pass
    def stackOverflow(self, entity): pass
    def damage(self, entity, attacker, damage, direct, effect): pass
    def summon(self, entity, summon): pass
    def useTP(self, tp): pass
    def heal(self, healer, entity, pv): pass
    def error(self, entity): pass
    def useChip(self, caster, chip, cell, targets, cellEntity): pass
    def useWeapon(self, caster, weapon, cell, targets, cellEntity): pass
    def kill(self, killer, entity, item, killCell): pass
    def critical(self, launcher): pass
    def endFight(self, values): pass
    def addTimes(self, current, time_, operations):
        self._opsByEntity[current.getFId()] = self._opsByEntity.get(current.getFId(), 0) + operations
    def move(self, mover, entity, start, path): pass
    def resurrect(self, caster, target): pass
    def getOperationsByEntity(self): return self._opsByEntity
    def tooMuchDebug(self, farmer): pass
    def show(self, mEntity, cell_id): pass
    def slide(self, entity, caster, start, cell): pass
    def useInvalidPosition(self, caster, attack, target): pass
    def effect(self, entity, caster, effect): pass
    def entityTurn(self, entity): pass
    def antidote(self, entity, caster, poisonsRemoved): pass
    def vitality(self, entity, caster, vitality): pass
    def registerWrite(self, entity, key, value): pass
    def setWeapon(self, entity, w): pass
    def chest(self): pass
    def chestKilled(self, killer, entity, resources): pass
