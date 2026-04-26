from ..state.entity import Entity


class Leek(Entity):

    def __init__(self, *args, **kwargs):
        # Two construction patterns mirror Java:
        # 1) Leek() - empty
        # 2) Leek(id, name) - simple
        # 3) Leek(id, name, farmer, level, life, ...)
        # 4) Leek(other_leek) - copy
        if len(args) == 0:
            super().__init__()
        elif len(args) == 2 and isinstance(args[0], (int, type(None))) and isinstance(args[1], str):
            super().__init__(args[0], args[1])
        elif len(args) == 1 and isinstance(args[0], Leek):
            super().__init__(args[0])
        else:
            super().__init__(*args, **kwargs)

    def getType(self) -> int:
        return Entity.TYPE_LEEK

    def getLeek(self):
        return self

    def isSummon(self) -> bool:
        return False
