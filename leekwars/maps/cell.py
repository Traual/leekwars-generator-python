class Cell:

    # __slots__ removes the per-instance __dict__: faster attribute access,
    # ~50% lower memory. With 613 cells per map and many state clones, it adds up.
    __slots__ = (
        "id", "walkable", "obstacle", "size",
        "north", "west", "east", "south",
        "x", "y", "composante",
        "visited", "closed", "cost", "weight", "parent",
    )

    def __init__(self, map_or_cell=None, id_=None):
        # Two constructor variants:
        # 1) (Map, int id) - new cell
        # 2) (Cell) - copy constructor
        if id_ is None:
            # Copy constructor
            cell = map_or_cell
            self.id = cell.id
            self.x = cell.x
            self.y = cell.y
            self.walkable = cell.walkable
            self.composante = cell.composante
            self.obstacle = cell.obstacle
            self.size = cell.size
            self.north = cell.north
            self.west = cell.west
            self.south = cell.south
            self.east = cell.east
            self.visited = False
            self.closed = False
            self.cost = 0
            self.weight = 0.0
            self.parent = None
            return

        map_ = map_or_cell
        self.id = id_
        self.walkable = True
        self.obstacle = 0
        self.size = 0
        self.north = True
        self.west = True
        self.east = True
        self.south = True
        self.composante = 0
        self.visited = False
        self.closed = False
        self.cost = 0
        self.weight = 0.0
        self.parent = None

        x = id_ % (map_.getWidth() * 2 - 1)
        y = id_ // (map_.getWidth() * 2 - 1)
        if y == 0 and x < map_.getWidth():
            self.north = False
            self.west = False
        elif y + 1 == map_.getHeight() and x >= map_.getWidth():
            self.east = False
            self.south = False
        if x == 0:
            self.south = False
            self.west = False
        elif x + 1 == map_.getWidth():
            self.north = False
            self.east = False

        # On calcule Y
        self.y = y - x % map_.getWidth()
        self.x = (id_ - (map_.getWidth() - 1) * self.y) // map_.getWidth()

    def hasNorth(self) -> bool:
        return self.north

    def hasSouth(self) -> bool:
        return self.south

    def hasWest(self) -> bool:
        return self.west

    def hasEast(self) -> bool:
        return self.east

    def isWalkable(self) -> bool:
        return self.walkable

    def getObstacle(self) -> int:
        return self.obstacle

    def getObstacleSize(self) -> int:
        return self.size

    def setWalkable(self, walkable: bool) -> None:
        self.walkable = walkable

    def setObstacle(self, id_: int, size: int) -> None:
        self.walkable = False
        self.obstacle = id_
        self.size = size

    def getId(self) -> int:
        return self.id

    def getX(self) -> int:
        return self.x

    def getY(self) -> int:
        return self.y

    def available(self, map_) -> bool:
        return self.walkable and map_.getEntity(self) is None

    def getPlayer(self, map_):
        return map_.getEntity(self)

    def getComposante(self) -> int:
        return self.composante

    def next(self, map_, dx: int, dy: int):
        return map_.getCell(self.x + dx, self.y + dy)

    def __repr__(self) -> str:
        return "<Cell " + str(self.id) + ">"

    def __str__(self) -> str:
        return self.__repr__()
