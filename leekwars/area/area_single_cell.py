from .area import Area


class AreaSingleCell(Area):

    def __init__(self, attack):
        super().__init__(attack)

    def getArea(self, map_, launchCell, targetCell, caster):
        area = []
        area.append(targetCell)
        return area
