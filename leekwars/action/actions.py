from ..util import json_util as Json


class Actions:

    def __init__(self, other=None):
        if other is not None:
            self.actions = list(other.actions)
        else:
            self.actions = []
        self.entities = []
        self.leeks = Json.create_array()
        self.map = Json.create_object()
        self.dead = Json.create_object()
        self.ops = Json.create_object()
        self.times = Json.create_object()
        self.mNextEffectId = 0

    def getEffectId(self) -> int:
        r = self.mNextEffectId
        self.mNextEffectId += 1
        return r

    def log(self, log) -> None:
        self.actions.append(log)

    def getNextId(self) -> int:
        return len(self.actions)

    def currentID(self) -> int:
        return len(self.actions) - 1

    def toJSON(self):
        json = Json.create_array()
        for log in self.actions:
            json.append(log.getJSON())
        retour = Json.create_object()
        retour["leeks"] = self.leeks
        retour["map"] = self.map
        retour["actions"] = json
        retour["dead"] = self.dead
        retour["ops"] = self.ops
        return retour

    def addOpsAndTimes(self, statistics) -> None:
        for entity_id, ops in statistics.getOperationsByEntity().items():
            self.ops[str(entity_id)] = ops

    def addEntity(self, entity, critical: bool) -> None:
        from ..state.entity import Entity
        self.entities.append(entity)

        obj = Json.create_object()
        obj["id"] = entity.getFId()
        obj["level"] = entity.getLevel()
        obj["skin"] = entity.getSkin()
        obj["hat"] = entity.getHat() if entity.getHat() > 0 else None
        obj["metal"] = entity.getMetal()
        obj["face"] = entity.getFace()

        obj["life"] = entity.getLife()
        obj["strength"] = entity.getStat(Entity.STAT_STRENGTH)
        obj["wisdom"] = entity.getStat(Entity.STAT_WISDOM)
        obj["agility"] = entity.getStat(Entity.STAT_AGILITY)
        obj["resistance"] = entity.getStat(Entity.STAT_RESISTANCE)
        obj["frequency"] = entity.getStat(Entity.STAT_FREQUENCY)
        obj["science"] = entity.getStat(Entity.STAT_SCIENCE)
        obj["magic"] = entity.getStat(Entity.STAT_MAGIC)
        obj["tp"] = entity.getTP()
        obj["mp"] = entity.getMP()

        obj["team"] = entity.getTeam() + 1
        obj["name"] = entity.getName()
        obj["cellPos"] = entity.getCell().getId() if entity.getCell() is not None else None
        obj["farmer"] = entity.getFarmer()
        obj["type"] = entity.getType()
        obj["orientation"] = entity.getOrientation()

        obj["summon"] = entity.isSummon()
        if entity.isSummon():
            obj["owner"] = entity.getSummoner().getFId()
            obj["critical"] = critical

        self.leeks.append(obj)

    def addMap(self, map_) -> None:
        obstacles = Json.create_object()
        for i in range((map_.getWidth() * 2 - 1) * map_.getHeight()):
            c = map_.getCell(i)
            if c is not None and not c.isWalkable() and c.getObstacleSize() > 0:
                if map_.getId() != 0:
                    obstacles[str(c.getId())] = c.getObstacle()
                else:
                    obstacle = Json.create_array()
                    obstacle.append(c.getObstacle())
                    obstacle.append(c.getObstacleSize())
                    if map_.isCustom():
                        obstacles[str(c.getId())] = obstacle
                    else:
                        obstacles[str(c.getId())] = c.getObstacleSize()
        if map_.getId() != 0:
            self.map["id"] = map_.getId()
        self.map["obstacles"] = obstacles
        self.map["type"] = map_.getType()
        self.map["width"] = map_.getWidth()
        self.map["height"] = map_.getWidth()
        if map_.getPattern() is not None:
            self.map["pattern"] = map_.getPattern()
