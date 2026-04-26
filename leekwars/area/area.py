from abc import ABC, abstractmethod


class Area(ABC):

    # Area types
    TYPE_SINGLE_CELL = 1
    TYPE_LASER_LINE = 2
    TYPE_CIRCLE1 = 3
    TYPE_CIRCLE2 = 4
    TYPE_CIRCLE3 = 5
    TYPE_AREA_PLUS_1 = 3  # Equals to CIRCLE_1
    TYPE_AREA_PLUS_2 = 6
    TYPE_AREA_PLUS_3 = 7
    TYPE_X_1 = 8
    TYPE_X_2 = 9
    TYPE_X_3 = 10
    TYPE_SQUARE_1 = 11
    TYPE_SQUARE_2 = 12
    TYPE_FIRST_IN_LINE = 13
    TYPE_ENEMIES = 14
    TYPE_ALLIES = 15

    def __init__(self, attack):
        self.mId = 0
        self.mAttack = attack

    @abstractmethod
    def getArea(self, map_, launchCell, targetCell, caster):
        pass

    def isAvailable(self, c, cells_to_ignore):
        if c.isWalkable():
            return True
        if cells_to_ignore is None:
            return False
        return c in cells_to_ignore

    @staticmethod
    def getAreaForType(attack, type_):
        # Imports here to avoid circular dependency
        from .area_single_cell import AreaSingleCell
        from .area_laser_line import AreaLaserLine
        from .area_circle1 import AreaCircle1
        from .area_circle2 import AreaCircle2
        from .area_circle3 import AreaCircle3
        from .area_plus2 import AreaPlus2
        from .area_plus3 import AreaPlus3
        from .area_x1 import AreaX1
        from .area_x2 import AreaX2
        from .area_x3 import AreaX3
        from .area_square1 import AreaSquare1
        from .area_square2 import AreaSquare2
        from .area_first_in_line import AreaFirstInLine
        from .area_allies import AreaAllies
        from .area_enemies import AreaEnemies

        if type_ == Area.TYPE_SINGLE_CELL:
            return AreaSingleCell(attack)
        elif type_ == Area.TYPE_LASER_LINE:
            return AreaLaserLine(attack)
        elif type_ == Area.TYPE_CIRCLE1 or type_ == Area.TYPE_AREA_PLUS_1:
            return AreaCircle1(attack)
        elif type_ == Area.TYPE_CIRCLE2:
            return AreaCircle2(attack)
        elif type_ == Area.TYPE_CIRCLE3:
            return AreaCircle3(attack)
        elif type_ == Area.TYPE_AREA_PLUS_2:
            return AreaPlus2(attack)
        elif type_ == Area.TYPE_AREA_PLUS_3:
            return AreaPlus3(attack)
        elif type_ == Area.TYPE_X_1:
            return AreaX1(attack)
        elif type_ == Area.TYPE_X_2:
            return AreaX2(attack)
        elif type_ == Area.TYPE_X_3:
            return AreaX3(attack)
        elif type_ == Area.TYPE_SQUARE_1:
            return AreaSquare1(attack)
        elif type_ == Area.TYPE_SQUARE_2:
            return AreaSquare2(attack)
        elif type_ == Area.TYPE_FIRST_IN_LINE:
            return AreaFirstInLine(attack)
        elif type_ == Area.TYPE_ALLIES:
            return AreaAllies(attack)
        elif type_ == Area.TYPE_ENEMIES:
            return AreaEnemies(attack)
        return None
