from .area import Area


class MaskArea(Area):

    def __init__(self, attack, area):
        super().__init__(attack)
        self.area = area

    def getArea(self, map_, launchCell, targetCell, caster):
        x, y = targetCell.getX(), targetCell.getY()
        cells = []
        for i in range(len(self.area)):
            c = map_.getCell(x + self.area[i][0], y + self.area[i][1])
            if c is None or not c.isWalkable():
                continue
            cells.append(c)
        return cells
