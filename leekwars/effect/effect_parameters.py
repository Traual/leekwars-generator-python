class EffectParameters:

    __slots__ = ("_id", "_value1", "_value2", "_turns", "_targets", "_modifiers")

    def __init__(self, id: int, value1: float, value2: float, turns: int, targets: int, modifiers: int):
        self._id = id
        self._value1 = value1
        self._value2 = value2
        self._turns = turns
        self._targets = targets
        self._modifiers = modifiers

    def getId(self) -> int:
        return self._id

    def getValue1(self) -> float:
        return self._value1

    def getValue2(self) -> float:
        return self._value2

    def getTurns(self) -> int:
        return self._turns

    def getTargets(self) -> int:
        return self._targets

    def getModifiers(self) -> int:
        return self._modifiers
