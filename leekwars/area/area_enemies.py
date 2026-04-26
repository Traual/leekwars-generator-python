from .area import Area


class AreaEnemies(Area):

    def __init__(self, attack):
        super().__init__(attack)

    def getArea(self, map_, launchCell, targetCell, caster):
        cells = []
        if caster is not None:
            for entity in map_.getState().getEntities().values():
                if entity.getCell() is not None and entity.getTeam() != caster.getTeam():
                    cells.append(entity.getCell())
        return cells
