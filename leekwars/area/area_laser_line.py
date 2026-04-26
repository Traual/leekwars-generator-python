from .area import Area


class AreaLaserLine(Area):

    def __init__(self, attack):
        super().__init__(attack)

    def getArea(self, map_, launchCell, targetCell, caster):
        cells = []
        dx, dy = 0, 0
        if launchCell.getX() == targetCell.getX():
            if launchCell.getY() > targetCell.getY():
                dy = -1
            else:
                dy = 1
        elif launchCell.getY() == targetCell.getY():
            if launchCell.getX() > targetCell.getX():
                dx = -1
            else:
                dx = 1
        else:
            return cells

        x, y = launchCell.getX(), launchCell.getY()
        for i in range(self.mAttack.getMinRange(), self.mAttack.getMaxRange() + 1):

            c = map_.getCell(x + dx * i, y + dy * i)
            if c is None:
                break
            if self.mAttack.needLos() and not c.isWalkable():
                break
            elif self.mAttack.needLos() and not c.isWalkable():
                break
            cells.append(c)
        return cells
