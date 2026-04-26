class Pathfinding:

    NORTH = 0  # NE
    EAST = 1  # SE
    SOUTH = 2  # SO
    WEST = 3  # NO

    DEBUG = False

    @staticmethod
    def inLine(c1, c2) -> bool:
        return c1.getX() == c2.getX() or c1.getY() == c2.getY()

    @staticmethod
    def getAverageDistance2(c1, cells) -> int:
        dist = 0
        for c2 in cells:
            dist += (c1.getX() - c2.getX()) * (c1.getX() - c2.getX()) + (c1.getY() - c2.getY()) * (c1.getY() - c2.getY())
        return dist // len(cells)

    @staticmethod
    def getCaseDistance(c1, c2_or_cells) -> int:
        # Two overloads: (Cell, Cell) and (Cell, List<Cell>)
        if isinstance(c2_or_cells, list):
            dist = -1
            for c2 in c2_or_cells:
                d = abs(c1.getX() - c2.getX()) + abs(c1.getY() - c2.getY())
                if dist == -1 or d < dist:
                    dist = d
            return dist
        c2 = c2_or_cells
        return abs(c1.getX() - c2.getX()) + abs(c1.getY() - c2.getY())


class Node:

    def __init__(self, cell, distance: float):
        self.cell = cell
        self.distance = int(distance)
        self.parcouru = 0
        self.parent = None
        self.poid = int(distance) * 5

    def setParent(self, parent, parcouru: int) -> None:
        self.parcouru = parcouru
        self.parent = parent
        self.poid = int(self.distance) * 5 + parcouru

    def getCell(self):
        return self.cell

    def getParcouru(self) -> int:
        return self.parcouru

    def getPoid(self) -> int:
        return self.poid

    def getParent(self):
        return self.parent
