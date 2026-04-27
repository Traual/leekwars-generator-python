import math
import random as py_random

from .cell import Cell
from .obstacle_info import ObstacleInfo
from .pathfinding import Pathfinding
from .mask_area_cell import MaskAreaCell


class Map:

    NORTH = 0  # NE
    EAST = 1  # SE
    SOUTH = 2  # SO
    WEST = 3  # NO

    DEBUG = False

    @staticmethod
    def generateMap(state, context, width, height, obstacles_count, teams, custom_map):
        from ..state.state import State
        from ..state.entity import Entity

        valid = False
        nb = 0
        map_ = None

        if custom_map is not None:
            mapId = custom_map["id"] if "id" in custom_map and custom_map["id"] is not None else 0
            map_ = Map(width, height, mapId)
            map_.custom_map = custom_map
            map_.pattern = custom_map.get("pattern")
            map_.state = state

            obstacles = custom_map.get("obstacles") or {}
            team1 = custom_map.get("team1")
            team2 = custom_map.get("team2")

            # Obstacles
            for c_key, c_value in obstacles.items():
                try:
                    cell_id = int(c_key)
                    cell = map_.getCell(cell_id)
                    if cell.available(map_):
                        if isinstance(c_value, bool):
                            cell.setObstacle(1, 1)
                        else:
                            id_ = int(c_value)
                            info = ObstacleInfo.get(id_)
                            if info.size == 1:
                                cell.setObstacle(id_, info.size)
                            elif info.size == 2:
                                cell.setObstacle(id_, info.size)
                                c2 = map_.getCellByDir(cell, Pathfinding.EAST)
                                c3 = map_.getCellByDir(cell, Pathfinding.SOUTH)
                                c4 = map_.getCellByDir(c3, Pathfinding.EAST)
                                c2.setObstacle(0, -1)
                                c3.setObstacle(0, -2)
                                c4.setObstacle(0, -3)
                            elif info.size == 3:
                                cell.setObstacle(id_, info.size)
                                for x in range(-1, 2):
                                    for y in range(-1, 2):
                                        if x != 0 or y != 0:
                                            map_.getNextCell(cell, x, y).setObstacle(0, -1)
                            elif info.size == 4:
                                cell.setObstacle(id_, info.size)
                                map_.getNextCell(cell, -3, 0).setObstacle(0, -1)
                            elif info.size == 5:
                                cell.setObstacle(id_, info.size)
                                map_.getNextCell(cell, 0, -1).setObstacle(0, -1)
                                map_.getNextCell(cell, 0, 3).setObstacle(0, -1)
                                map_.getNextCell(cell, 2, -1).setObstacle(0, -1)
                                map_.getNextCell(cell, 2, 0).setObstacle(0, -1)
                                map_.getNextCell(cell, 2, 3).setObstacle(0, -1)
                except Exception as e:
                    pass

            # Set entities positions
            for t in range(len(teams)):
                pos = 0
                for l in teams[t].getEntities():
                    if l.isDead():
                        continue
                    c = None
                    if map_.id != 0 and l.getInitialCell() is not None:
                        c = map_.getCell(l.getInitialCell())
                    else:
                        if len(teams) == 2:
                            c = map_.getRandomCell(state, 1 if t == 0 else 4)
                        else:
                            c = map_.getRandomCell(state)
                        if t < 2:
                            team = team1 if t == 0 else team2
                            if team is not None:
                                if pos < len(team):
                                    cell_id = int(team[pos])
                                    pos += 1
                                    if cell_id >= 0 or cell_id < map_.nb_cells:
                                        c = map_.getCell(cell_id)
                    if c is not None:
                        map_.setEntity(l, c)

            map_.computeComposantes()
        else:
            while not valid and nb < 63:
                nb += 1
                map_ = Map(width, height)
                map_.state = state

                for i in range(obstacles_count):
                    c = map_.getCell(state.getRandom().get_int(0, map_.getNbCell()))
                    if c is not None and c.available(map_):
                        size = state.getRandom().get_int(1, 2)
                        type_ = state.getRandom().get_int(0, 2)
                        if size == 2:
                            c2 = map_.getCellByDir(c, Pathfinding.EAST)
                            c3 = map_.getCellByDir(c, Pathfinding.SOUTH)
                            c4 = map_.getCellByDir(c3, Pathfinding.EAST) if c3 is not None else None
                            if c2 is None or c3 is None or c4 is None or not c2.available(map_) or not c3.available(map_) or not c4.available(map_):
                                size = 1
                            else:
                                c2.setObstacle(0, -1)
                                c3.setObstacle(0, -2)
                                c4.setObstacle(0, -3)
                        c.setObstacle(type_, size)
                map_.computeComposantes()
                leeks = []

                for t in range(len(teams)):
                    for l in teams[t].getEntities():
                        c = None
                        if state.getType() == State.TYPE_BATTLE_ROYALE:
                            c = map_.getRandomCell(state)
                        else:
                            if state.getType() == State.TYPE_CHEST_HUNT:
                                if l.getType() == Entity.TYPE_CHEST:
                                    c = map_.getRandomCellNearCenter(state, 3)
                                else:
                                    c = map_.getRandomCellAwayFromCenter(state, 12)
                            elif l.getType() == Entity.TYPE_CHEST:
                                team0HasCells = any(e.getCell() is not None for e in state.getTeamEntities(0))
                                team1HasCells = len(teams) > 1 and any(e.getCell() is not None for e in state.getTeamEntities(1))
                                c = map_.getCellEqualDistance(state) if (team0HasCells and team1HasCells) else map_.getRandomCell(state)
                            else:
                                c = map_.getRandomCell(state, 1 if t == 0 else 4)
                        if c is None:
                            continue

                        map_.setEntity(l, c)
                        leeks.append(l)

                        if l.getType() == Entity.TYPE_TURRET:
                            for cell in map_.getCellsInCircle(c, 5):
                                map_.removeObstacle(cell)

                # Check paths
                valid = True
                if len(leeks) > 0:
                    composante = map_.getEntityCell(leeks[0]).getComposante()
                    for i in range(1, len(leeks)):
                        if composante != map_.getEntityCell(leeks[i]).getComposante():
                            valid = False
                            break

        # Generate type
        map_.setType(state.getRandom().get_int(0, 4))

        if context == State.CONTEXT_TEST:
            map_.setType(-1)  # Nexus
        elif context == State.CONTEXT_TOURNAMENT:
            map_.setType(5)  # Arena
        elif custom_map is not None and "type" in custom_map:
            map_.setType(int(custom_map["type"]))
        return map_

    def __init__(self, width, height, id_=0):
        self.width = width
        self.height = height
        self.id = id_

        self.nb_cells = (width * 2 - 1) * height - (width - 1)

        self.cells = []
        self.min_x = -1
        self.max_x = -1
        self.min_y = -1
        self.max_y = -1
        for i in range(self.nb_cells):
            c = Cell(self, i)
            self.cells.append(c)
            if self.min_x == -1 or c.getX() < self.min_x:
                self.min_x = c.getX()
            if self.max_x == -1 or c.getX() > self.max_x:
                self.max_x = c.getX()
            if self.min_y == -1 or c.getY() < self.min_y:
                self.min_y = c.getY()
            if self.max_y == -1 or c.getY() > self.max_y:
                self.max_y = c.getY()
        sx = self.max_x - self.min_x + 1
        sy = self.max_y - self.min_y + 1
        self.coord = [[None for _ in range(sy)] for _ in range(sx)]
        for i in range(self.nb_cells):
            c = self.cells[i]
            self.coord[c.getX() - self.min_x][c.getY() - self.min_y] = c

        self.type = 0
        self.mObstacles = None
        self.custom_map = None
        self.pattern = None
        self.state = None
        self.cellByEntity = {}
        self.entityByCell = {}
        self._path_cache = {}  # invalidated by positionChanged()

        # Pre-compute the 4-neighbour table once. The grid is static, so
        # this is much faster than calling getCellByDir 4 times per query.
        # We inline getCellByDir to skip method-call + branch overhead.
        cells = self.cells
        nb = self.nb_cells
        w = self.width
        self._neighbors = [None] * nb
        for c in cells:
            cid = c.id
            south = cells[cid + w - 1] if c.south and (cid + w - 1) < nb else None
            west = cells[cid - w] if c.west and (cid - w) >= 0 else None
            north = cells[cid - w + 1] if c.north and (cid - w + 1) >= 0 else None
            east = cells[cid + w] if c.east and (cid + w) < nb else None
            self._neighbors[cid] = (south, west, north, east)

    @staticmethod
    def copy(map_, state):
        new_map = Map.__new__(Map)
        new_map.id = map_.id
        new_map.width = map_.width
        new_map.height = map_.height
        new_map.nb_cells = map_.nb_cells
        new_map.cells = map_.cells
        new_map.coord = map_.coord
        new_map.min_x = map_.min_x
        new_map.max_x = map_.max_x
        new_map.min_y = map_.min_y
        new_map.max_y = map_.max_y
        new_map.type = map_.type
        new_map.mObstacles = None
        new_map.custom_map = map_.custom_map
        new_map.pattern = map_.pattern
        new_map.state = state
        new_map.cellByEntity = {}
        new_map.entityByCell = {}
        for cell, entity in map_.entityByCell.items():
            new_map.entityByCell[cell] = state.getEntity(entity.getFId())
        for entity, cell in map_.cellByEntity.items():
            new_map.cellByEntity[state.getEntity(entity.getFId())] = cell
        return new_map

    def setEntity(self, entity, cell) -> None:
        self.entityByCell[cell] = entity
        self.cellByEntity[entity] = cell
        entity.setCell(cell)
        self.positionChanged()

    def moveEntity(self, entity, cell) -> None:
        oldCell = self.cellByEntity.pop(entity, None)
        if oldCell is not None:
            self.entityByCell.pop(oldCell, None)
        self.entityByCell[cell] = entity
        self.cellByEntity[entity] = cell
        entity.setCell(cell)
        self.positionChanged()

    def removeEntity(self, entity) -> None:
        cell = self.cellByEntity.pop(entity, None)
        if cell is not None:
            self.entityByCell.pop(cell, None)
        entity.setCell(None)
        self.positionChanged()

    def invertEntities(self, entity1, entity2) -> None:
        cell1 = self.cellByEntity.get(entity1)
        cell2 = self.cellByEntity.get(entity2)
        self.cellByEntity[entity1] = cell2
        self.cellByEntity[entity2] = cell1
        self.entityByCell[cell1] = entity2
        self.entityByCell[cell2] = entity1
        entity1.setCell(cell2)
        entity2.setCell(cell1)

    def getNbCell(self) -> int:
        return self.nb_cells

    def getType(self) -> int:
        return self.type

    def setType(self, type_: int) -> None:
        self.type = type_

    def getCell(self, *args):
        if len(args) == 1:
            id_ = args[0]
            if id_ < 0 or id_ >= len(self.cells):
                return None
            return self.cells[id_]
        x, y = args
        try:
            ix = x - self.min_x
            iy = y - self.min_y
            if ix < 0 or iy < 0:
                return None
            return self.coord[ix][iy]
        except IndexError:
            return None

    def getCells(self):
        return self.cells

    def getNextCell(self, cell, dx, dy):
        x = cell.x + dx
        y = cell.y + dy
        if x < self.min_x or y < self.min_y or x > self.max_x or y > self.max_y:
            return None
        return self.coord[x - self.min_x][y - self.min_y]

    def getObstacles(self):
        if self.mObstacles is None:
            obstacles = []
            for c in self.cells:
                if not c.isWalkable():
                    obstacles.append(c)
            self.mObstacles = obstacles
        return self.mObstacles

    def getWidth(self) -> int:
        return self.width

    def getHeight(self) -> int:
        return self.height

    def clear(self) -> None:
        for c in self.cells:
            c.setObstacle(0, 0)
            c.setWalkable(True)

    def getRandomCell(self, state, part=None):
        if part is None:
            retour = None
            nb = 0
            while retour is None or not retour.available(self):
                retour = self.getCell(state.getRandom().get_int(0, self.nb_cells))
                nb += 1
                if nb > 64:
                    break
            return retour
        retour = None
        nb = 0
        while retour is None or not retour.available(self):
            y = state.getRandom().get_int(0, self.height - 1)
            x = state.getRandom().get_int(0, self.width // 4)
            cellid = y * (self.width * 2 - 1)
            cellid += (part - 1) * self.width // 4 + x
            retour = self.getCell(cellid)
            nb += 1
            if nb > 64:
                break
        return retour

    def getCellEqualDistance(self, state):
        possible = []
        for cell in self.cells:
            if cell.available(self) and abs(self.getDistanceWithTeam(state, 0, cell) - self.getDistanceWithTeam(state, 1, cell)) < 2:
                possible.append(cell)
        if len(possible) > 0:
            i = state.getRandom().get_int(0, len(possible) - 1)
            return possible[i]
        return self.getRandomCell(state)

    def getCellsEqualDistance(self, cell1, cell2):
        result = []
        for cell in self.cells:
            if cell.isWalkable() and abs(Pathfinding.getCaseDistance(cell, cell1) - Pathfinding.getCaseDistance(cell, cell2)) < 2:
                result.append(cell)
        return result

    def getDistanceWithTeam(self, state, team, cell):
        min_d = 2 ** 31 - 1
        for entity in state.getTeamEntities(team):
            d = Pathfinding.getCaseDistance(entity.getCell(), cell)
            if d < min_d:
                min_d = d
        return min_d

    def getTeamBarycenter(self, state, team):
        tx = 0
        ty = 0
        entities = state.getTeamEntities(team)
        for entity in entities:
            tx += entity.getCell().x
            ty += entity.getCell().y
        from ..util.java_math import java_div
        return self.getCell(java_div(tx, len(entities)), java_div(ty, len(entities)))

    def getRandomCellNearCenter(self, state, maxDistance):
        center = self.getCell(self.nb_cells // 2)
        possible = []
        for cell in self.cells:
            if cell.available(self) and Pathfinding.getCaseDistance(cell, center) <= maxDistance:
                possible.append(cell)
        if len(possible) > 0:
            return possible[state.getRandom().get_int(0, len(possible) - 1)]
        return self.getRandomCell(state)

    def getRandomCellAwayFromCenter(self, state, minDistance):
        center = self.getCell(self.nb_cells // 2)
        possible = []
        for cell in self.cells:
            if cell.available(self) and Pathfinding.getCaseDistance(cell, center) >= minDistance:
                possible.append(cell)
        if len(possible) > 0:
            return possible[state.getRandom().get_int(0, len(possible) - 1)]
        return self.getRandomCell(state)

    def getRandomCellAtDistance(self, cell1, distance):
        result = []
        for cell in self.cells:
            if cell.isWalkable() and Pathfinding.getCaseDistance(cell, cell1) == distance:
                result.append(cell)
        if len(result) == 0:
            return None
        return result[int(len(result) * py_random.random())]

    def computeComposantes(self) -> None:
        connexe = [[-1 for _ in range(len(self.coord[0]))] for _ in range(len(self.coord))]
        ni = 1
        for x in range(len(connexe)):
            for y in range(len(connexe[x])):
                c = self.coord[x][y]
                if c is None:
                    continue
                cur_number = 0
                if x > 0 and self.coord[x - 1][y] is not None and self.coord[x - 1][y].isWalkable() == c.isWalkable():
                    cur_number = connexe[x - 1][y]

                if y > 0 and self.coord[x][y - 1] is not None and self.coord[x][y - 1].isWalkable() == c.isWalkable():
                    if cur_number == 0:
                        cur_number = connexe[x][y - 1]
                    elif cur_number != connexe[x][y - 1]:
                        target_number = connexe[x][y - 1]
                        for x2 in range(len(connexe)):
                            for y2 in range(y + 1):
                                if connexe[x2][y2] == target_number:
                                    connexe[x2][y2] = cur_number

                if cur_number == 0:
                    connexe[x][y] = ni
                    ni += 1
                else:
                    connexe[x][y] = cur_number
        for cell in self.cells:
            cell.composante = connexe[cell.getX() - self.min_x][cell.getY() - self.min_y]

    def getPathBeetween(self, start, end, cells_to_ignore):
        if start is None or end is None:
            return None
        # Try the per-turn cache first (only for the common no-ignore case
        # — anything more is too rare to bother caching).
        if cells_to_ignore is None:
            key = (start.id, end.id)
            cache = getattr(self, "_path_cache", None)
            if cache is not None and key in cache:
                cached = cache[key]
                # Return a fresh list so callers can mutate it freely.
                return list(cached) if cached is not None else None
            r = self.getAStarPath(start, [end], None)
            if cache is not None:
                cache[key] = r
            return r
        return self.getAStarPath(start, [end], cells_to_ignore)

    def positionChanged(self) -> None:
        # Java has this hook for invalidating path caches. We use it the same way.
        if hasattr(self, "_path_cache"):
            self._path_cache.clear()

    # Public hook used by the State at start-of-turn to enable path caching.
    def beginTurnCache(self) -> None:
        self._path_cache = {}

    def endTurnCache(self) -> None:
        self._path_cache = None

    def getCellsInCircle(self, cell, radius):
        cells = []
        for x in range(cell.x - radius, cell.x + radius + 1):
            for y in range(cell.y - radius, cell.y + radius + 1):
                c = self.getCell(x, y)
                if c is not None:
                    cells.append(c)
        return cells

    def removeObstacle(self, cell) -> None:
        if cell.getObstacleSize() > 0:
            if cell.getObstacleSize() == 2:
                c2 = self.getCellByDir(cell, Pathfinding.EAST)
                c3 = self.getCellByDir(cell, Pathfinding.SOUTH)
                c4 = self.getCellByDir(c3, Pathfinding.EAST)
                c2.setObstacle(0, 0)
                c2.setWalkable(True)
                c3.setObstacle(0, 0)
                c3.setWalkable(True)
                c4.setObstacle(0, 0)
                c4.setWalkable(True)
            cell.setObstacle(0, 0)
            cell.setWalkable(True)

    def isCustom(self) -> bool:
        return self.custom_map is not None

    def getEntity(self, cell):
        return self.entityByCell.get(cell)

    def getEntityCell(self, entity):
        return self.cellByEntity.get(entity)

    def getCellByDir(self, c, dir_):
        if c is None:
            return None
        if dir_ == Map.NORTH and c.hasNorth():
            return self.getCell(c.getId() - self.width + 1)
        elif dir_ == Map.WEST and c.hasWest():
            return self.getCell(c.getId() - self.width)
        elif dir_ == Map.EAST and c.hasEast():
            return self.getCell(c.getId() + self.width)
        elif dir_ == Map.SOUTH and c.hasSouth():
            return self.getCell(c.getId() + self.width - 1)
        return None

    def verifyLoS(self, start, end, attack, ignoredCells=None):
        from ..area.area import Area
        if ignoredCells is None:
            ignoredCells = []
            ignoredCells.append(start)

            # Ignore first entity in area for Area first in line
            if attack.getArea() == Area.TYPE_FIRST_IN_LINE:
                cell = self.getFirstEntity(start, end, attack.getMinRange(), attack.getMaxRange())
                if cell is end:
                    return False
                if cell is not None:
                    ignoredCells.append(cell)
            return self.verifyLoS(start, end, attack, ignoredCells)

        needLos = True if attack is None else attack.needLos()
        if not needLos:
            return True

        a = abs(start.getY() - end.getY())
        b = abs(start.getX() - end.getX())
        dx = -1 if start.getX() > end.getX() else 1
        dy = 1 if start.getY() < end.getY() else -1
        path = []

        if b == 0:
            path.append(0)
            path.append(a + 1)
        else:
            d = a / b / 2.0
            h = 0
            for i in range(b):
                y = 0.5 + (i * 2 + 1) * d
                path.append(h)
                path.append(int(math.ceil(y - 0.00001)) - h)
                h = int(math.floor(y + 0.00001))
            path.append(h)
            path.append(a + 1 - h)

        for p in range(0, len(path), 2):
            for i in range(path[p + 1]):
                cell = self.getCell(start.getX() + (p // 2) * dx, start.getY() + (path[p] + i) * dy)
                if cell is None:
                    return False
                if needLos:
                    if not cell.isWalkable():
                        return False
                    if not cell.available(self):
                        if cell.getId() == start.getId():
                            continue
                        if cell.getId() == end.getId():
                            return True
                        if cell not in ignoredCells:
                            return False
        return True

    def getCellsAround(self, c):
        # Use the pre-computed table (same SOUTH/WEST/NORTH/EAST order Java uses).
        return self._neighbors[c.id]

    def getPathTowardLine(self, start, linecell1, linecell2):
        line_cell = []
        dx_v = linecell2.getX() - linecell1.getX()
        dy_v = linecell2.getY() - linecell1.getY()
        dx = (1 if dx_v > 0 else (-1 if dx_v < 0 else 0))
        dy = (1 if dy_v > 0 else (-1 if dy_v < 0 else 0))
        if dx == 0 and dy == 0:
            return None
        curent = linecell1
        while curent is not None:
            line_cell.append(curent)
            curent = self.getCell(curent.getX() + dx, curent.getY() + dy)
        curent = self.getCell(linecell1.getX() - dx, linecell1.getY() - dy)
        while curent is not None:
            line_cell.append(curent)
            curent = self.getCell(curent.getX() - dx, curent.getY() - dy)
        return self.getAStarPath(start, line_cell)

    def getPathAwayFromLine(self, start, linecell1, linecell2, max_distance):
        if start is None:
            return None
        line_cell = []
        dx_v = linecell2.getX() - linecell1.getX()
        dy_v = linecell2.getY() - linecell1.getY()
        dx = (1 if dx_v > 0 else (-1 if dx_v < 0 else 0))
        dy = (1 if dy_v > 0 else (-1 if dy_v < 0 else 0))
        if dx == 0 and dy == 0:
            return None
        current = linecell1
        while current is not None:
            line_cell.append(current)
            current = self.getCell(current.getX() + dx, current.getY() + dy)
        current = self.getCell(linecell1.getX() - dx, linecell1.getY() - dy)
        while current is not None:
            line_cell.append(current)
            current = self.getCell(current.getX() - dx, current.getY() - dy)
        return self.getPathAway(start, line_cell, max_distance)

    def getPathAway(self, start, bad_cells, max_distance):
        if start is None:
            return None
        curent_distance = self.getDistance2_list(start, bad_cells)
        potential_targets = []
        cells = MaskAreaCell.generateCircleMask(1, max_distance)
        if cells is None:
            return None
        x = start.getX()
        y = start.getY()
        for i in range(len(cells)):
            c = self.getCell(x + cells[i][0], y + cells[i][1])
            if c is None or not c.available(self):
                continue
            distance = self.getDistance2_list(c, bad_cells)
            if distance > curent_distance:
                potential_targets.append((c, distance))
        if len(potential_targets) == 0:
            return None
        potential_targets.sort(key=lambda cd: -cd[1])
        path = None
        for c, _ in potential_targets:
            path = self.getAStarPath(start, [c])
            if path is not None and len(path) <= max_distance:
                break
            else:
                path = None
        return path

    def getDistance2_list(self, c1, cells):
        dist = -1
        for c2 in cells:
            d = (c1.getX() - c2.getX()) ** 2 + (c1.getY() - c2.getY()) ** 2
            if dist == -1 or d < dist:
                dist = d
        return dist

    def getPathAwayMin(self, map_, start, bad_cells, max_distance):
        curent_distance = self.getDistance2_list(start, bad_cells)
        potential_targets = []
        cells = MaskAreaCell.generateCircleMask(1, max_distance)
        x = start.getX()
        y = start.getY()
        for i in range(len(cells)):
            c = map_.getCell(x + cells[i][0], y + cells[i][1])
            if c is None or not c.available(map_):
                continue
            distance = self.getDistance2_list(c, bad_cells)
            if distance > curent_distance:
                potential_targets.append((c, distance))
        if len(potential_targets) == 0:
            return None
        potential_targets.sort(key=lambda cd: -cd[1])
        path = None
        for c, _ in potential_targets:
            path = self.getAStarPath(start, [c])
            if path is not None and len(path) <= max_distance:
                break
            else:
                path = None
        return path

    def available(self, c, cells_to_ignore) -> bool:
        if c is None:
            return False
        if c.available(self):
            return True
        if cells_to_ignore is not None and c in cells_to_ignore:
            return True
        return False

    def getAStarPath(self, c1, endCells, cells_to_ignore=None):
        if c1 is None or endCells is None or len(endCells) == 0:
            return None
        if c1 in endCells:
            return None

        for c in self.getCells():
            c.visited = False
            c.closed = False
            c.cost = 32767  # Short.MAX_VALUE

        # Java uses a TreeSet with a comparator that returns -1 for equal weights,
        # which makes ties LIFO (the most recently inserted equal-weight cell wins
        # the next pollFirst()). We replicate that with a min-heap whose secondary
        # key is a *decreasing* counter.
        import heapq
        heap = []
        counter = [0]

        def push(cell):
            heapq.heappush(heap, (cell.weight, -counter[0], cell))
            counter[0] += 1

        c1.cost = 0
        c1.weight = 0
        c1.visited = True
        push(c1)

        while len(heap) > 0:
            _, _, u = heapq.heappop(heap)
            if u.closed:
                continue
            u.closed = True

            if u in endCells:
                result = []
                s = u.cost
                while s >= 1:
                    result.append(u)
                    u = u.parent
                    s -= 1
                result.reverse()
                last = result[len(result) - 1]
                if last.getPlayer(self) is not None and (cells_to_ignore is None or last not in cells_to_ignore):
                    result.pop()
                return result

            for c in self.getCellsAround(u):
                if c is None or c.closed or not c.isWalkable():
                    continue
                if c.getPlayer(self) is not None and (cells_to_ignore is None or c not in cells_to_ignore) and c not in endCells:
                    continue

                if not c.visited or u.cost + 1 < c.cost:
                    c.cost = u.cost + 1
                    c.weight = c.cost + Map.getDistance(c, endCells[0])
                    c.parent = u
                    if not c.visited:
                        push(c)
                        c.visited = True
        return None

    def getPossibleCastCellsForTarget(self, attack, target, cells_to_ignore):
        from ..attack.attack import Attack
        if target is None:
            return None
        possible = []

        if target.isWalkable():
            if attack.getLaunchType() == Attack.LAUNCH_TYPE_LINE:
                line = [True, True, True, True]
                x = target.getX()
                y = target.getY()
                dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]]
                for i in range(0, attack.getMaxRange() + 1):
                    for dir_ in range(4):
                        if not line[dir_]:
                            continue
                        c = self.getCell(x + i * dirs[dir_][0], y + i * dirs[dir_][1])
                        if c is None:
                            line[dir_] = False
                        else:
                            if attack.needLos() and not self.available(c, cells_to_ignore) and i > 0:
                                line[dir_] = False
                            elif attack.needLos() and not c.isWalkable():
                                line[dir_] = False
                            elif attack.getMinRange() <= i and self.available(c, cells_to_ignore):
                                possible.append(c)
            else:
                mask = MaskAreaCell.generateMask(attack.getLaunchType(), attack.getMinRange(), attack.getMaxRange())
                x = target.getX()
                y = target.getY()
                for mask_cell in mask:
                    cell = self.getCell(x + mask_cell[0], y + mask_cell[1])
                    if cell is None or not self.available(cell, cells_to_ignore):
                        continue
                    if not self.verifyLoS(cell, target, attack, cells_to_ignore):
                        continue
                    possible.append(cell)
        return possible

    def getFirstEntity(self, from_cell, target, minRange, maxRange):
        dx_v = target.x - from_cell.x
        dy_v = target.y - from_cell.y
        dx = (1 if dx_v > 0 else (-1 if dx_v < 0 else 0))
        dy = (1 if dy_v > 0 else (-1 if dy_v < 0 else 0))
        current = from_cell.next(self, dx, dy)
        range_ = 1
        while current is not None and current.isWalkable() and range_ <= maxRange:
            if range_ >= minRange and self.getEntity(current) is not None:
                return current
            current = current.next(self, dx, dy)
            range_ += 1
        return None

    def getPushLastAvailableCell(self, entity, target, caster):
        cdx_v = entity.x - caster.x
        cdy_v = entity.y - caster.y
        cdx = (1 if cdx_v > 0 else (-1 if cdx_v < 0 else 0))
        cdy = (1 if cdy_v > 0 else (-1 if cdy_v < 0 else 0))
        dx_v = target.x - entity.x
        dy_v = target.y - entity.y
        dx = (1 if dx_v > 0 else (-1 if dx_v < 0 else 0))
        dy = (1 if dy_v > 0 else (-1 if dy_v < 0 else 0))
        if cdx != dx or cdy != dy:
            return entity
        current = entity
        while current is not target:
            next_ = current.next(self, dx, dy)
            if not next_.available(self):
                return current
            current = next_
        return current

    def getAttractLastAvailableCell(self, entity, target, caster):
        cdx_v = entity.x - caster.x
        cdy_v = entity.y - caster.y
        cdx = (1 if cdx_v > 0 else (-1 if cdx_v < 0 else 0))
        cdy = (1 if cdy_v > 0 else (-1 if cdy_v < 0 else 0))
        dx_v = target.x - entity.x
        dy_v = target.y - entity.y
        dx = (1 if dx_v > 0 else (-1 if dx_v < 0 else 0))
        dy = (1 if dy_v > 0 else (-1 if dy_v < 0 else 0))
        if cdx != -dx or cdy != -dy:
            return entity
        current = entity
        while current is not target:
            next_ = current.next(self, dx, dy)
            if not next_.available(self):
                return current
            current = next_
        return current

    def canUseAttack(self, caster, target, attack) -> bool:
        if not self.verifyRange(caster, target, attack):
            return False
        return self.verifyLoS(caster, target, attack)

    def verifyRange(self, caster, target, attack) -> bool:
        if target is None or caster is None:
            return False
        dx = caster.getX() - target.getX()
        dy = caster.getY() - target.getY()
        distance = abs(dx) + abs(dy)

        if distance > attack.getMaxRange() or distance < attack.getMinRange():
            return False
        if caster is target:
            return True

        if (attack.getLaunchType() & 1) == 0 and (dx == 0 or dy == 0):
            return False
        if (attack.getLaunchType() & 2) == 0 and abs(dx) == abs(dy):
            return False
        if (attack.getLaunchType() & 4) == 0 and abs(dx) != abs(dy) and dx != 0 and dy != 0:
            return False
        return True

    def getValidCellsAroundObstacle(self, cell):
        retour = []
        size = 1
        close = []
        close.append(cell)
        for i in range(1, size + 1):
            stop = True
            for j in range(i):
                stop = self._addValidCell(retour, close, self.getCell(cell.getX() + j, cell.getY() + (i - j)), cell) and stop
                stop = self._addValidCell(retour, close, self.getCell(cell.getX() - j, cell.getY() - (i - j)), cell) and stop
                stop = self._addValidCell(retour, close, self.getCell(cell.getX() + i - j, cell.getY() - j), cell) and stop
                stop = self._addValidCell(retour, close, self.getCell(cell.getX() - i + j, cell.getY() + j), cell) and stop
            if not stop and size < 5:
                size += 1
        return retour

    def _addValidCell(self, retour, close, c, center) -> bool:
        if c is None:
            return True
        dx_v = center.getX() - c.getX()
        dy_v = center.getY() - c.getY()
        dx = (1 if dx_v > 0 else (-1 if dx_v < 0 else 0))
        dy = (1 if dy_v > 0 else (-1 if dy_v < 0 else 0))

        c1 = self.getCell(c.getX() + dx, c.getY())
        c2 = self.getCell(c.getX(), c.getY() + dy)

        if not c.isWalkable():
            if (c1 is not None and not c1.isWalkable() and c1 in close) or (c2 is not None and not c2.isWalkable() and c2 in close):
                close.append(c)
                return False
        else:
            if (c1 is not None and not c1.isWalkable() and c1 in close) or (c2 is not None and not c2.isWalkable() and c2 in close):
                retour.append(c)
        return True

    @staticmethod
    def getDistance(c1, c2) -> float:
        return math.sqrt(Map.getDistance2(c1, c2))

    @staticmethod
    def getDistance2(c1, c2) -> int:
        return (c1.getX() - c2.getX()) * (c1.getX() - c2.getX()) + (c1.getY() - c2.getY()) * (c1.getY() - c2.getY())

    def getId(self) -> int:
        return self.id

    def getPattern(self):
        return self.pattern

    def getState(self):
        return self.state

    def getEntities(self):
        return self.cellByEntity
