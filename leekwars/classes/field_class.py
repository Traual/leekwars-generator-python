"""Python port of FieldClass - cell/map utilities."""

from ..maps.map import Map
from ..maps.pathfinding import Pathfinding


def getMapType(ai) -> int:
    return ai.getState().getMap().getType()


def getMapID(ai) -> int:
    return ai.getState().getMap().getId()


def getMap(ai) -> int:
    return ai.getState().getMap().getId()


def getCellX(ai, cell_id):
    cell = ai.getState().getMap().getCell(int(cell_id))
    if cell is None:
        return None
    return cell.getX()


def getCellY(ai, cell_id):
    cell = ai.getState().getMap().getCell(int(cell_id))
    if cell is None:
        return None
    return cell.getY()


def getCellFromXY(ai, x, y):
    cell = ai.getState().getMap().getCell(int(x), int(y))
    if cell is None:
        return None
    return cell.getId()


def getDistance(ai, cell1_id, cell2_id):
    c1 = ai.getState().getMap().getCell(int(cell1_id))
    c2 = ai.getState().getMap().getCell(int(cell2_id))
    if c1 is None or c2 is None:
        return None
    return Map.getDistance(c1, c2)


def getCellDistance(ai, cell1_id, cell2_id):
    c1 = ai.getState().getMap().getCell(int(cell1_id))
    c2 = ai.getState().getMap().getCell(int(cell2_id))
    if c1 is None or c2 is None:
        return None
    return Pathfinding.getCaseDistance(c1, c2)


def getPath(ai, cell1_id, cell2_id, ignored_cells=None):
    c1 = ai.getState().getMap().getCell(int(cell1_id))
    c2 = ai.getState().getMap().getCell(int(cell2_id))
    if c1 is None or c2 is None:
        return None
    ignored = []
    if ignored_cells is not None:
        for v in ignored_cells:
            cell = ai.getState().getMap().getCell(int(v))
            if cell is not None:
                ignored.append(cell)
    path = ai.getState().getMap().getAStarPath(c1, [c2], ignored)
    if path is None:
        return None
    return [c.getId() for c in path]


def getPathLength(ai, cell1_id, cell2_id, ignored_cells=None):
    path = getPath(ai, cell1_id, cell2_id, ignored_cells)
    if path is None:
        return None
    return len(path)


def isOnSameLine(ai, cell1_id, cell2_id) -> bool:
    c1 = ai.getState().getMap().getCell(int(cell1_id))
    c2 = ai.getState().getMap().getCell(int(cell2_id))
    if c1 is None or c2 is None:
        return False
    return Pathfinding.inLine(c1, c2)


def lineOfSight(ai, cell1_id, cell2_id, ignored_cells=None) -> bool:
    c1 = ai.getState().getMap().getCell(int(cell1_id))
    c2 = ai.getState().getMap().getCell(int(cell2_id))
    if c1 is None or c2 is None:
        return False
    ignored = [c1]
    if ignored_cells is not None:
        for v in ignored_cells:
            cell = ai.getState().getMap().getCell(int(v))
            if cell is not None:
                ignored.append(cell)
    return ai.getState().getMap().verifyLoS(c1, c2, None, ignored)


def isEmptyCell(ai, cell_id) -> bool:
    cell = ai.getState().getMap().getCell(int(cell_id))
    if cell is None:
        return False
    return cell.available(ai.getState().getMap())


def isLeekOnCell(ai, cell_id) -> bool:
    cell = ai.getState().getMap().getCell(int(cell_id))
    if cell is None:
        return False
    return cell.getPlayer(ai.getState().getMap()) is not None


def isObstacle(ai, cell_id) -> bool:
    cell = ai.getState().getMap().getCell(int(cell_id))
    if cell is None:
        return True
    return not cell.isWalkable()


def getLeekOnCell(ai, cell_id):
    cell = ai.getState().getMap().getCell(int(cell_id))
    if cell is None:
        return -1
    player = cell.getPlayer(ai.getState().getMap())
    if player is None:
        return -1
    return player.getFId()


def getObstacles(ai):
    return [c.getId() for c in ai.getState().getMap().getObstacles()]


def getLeekCell(ai, leek_id):
    e = ai.getFight().getEntity(leek_id)
    if e is None or e.getCell() is None:
        return None
    return e.getCell().getId()
