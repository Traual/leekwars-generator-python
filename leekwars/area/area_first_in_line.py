from .area import Area


class AreaFirstInLine(Area):

    def __init__(self, attack):
        super().__init__(attack)

    def getArea(self, map_, launchCell, targetCell, caster):
        cells = []
        cell = map_.getFirstEntity(launchCell, targetCell, self.mAttack.getMinRange(), self.mAttack.getMaxRange())
        if cell is not None:
            cells.append(cell)
        return cells
