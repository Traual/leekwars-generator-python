from .area import Area


class AreaAllies(Area):

    def __init__(self, attack):
        super().__init__(attack)

    def getArea(self, map_, launchCell, targetCell, caster):
        cells = []
        if caster is not None:
            for entity in map_.getState().getEntities().values():
                if entity.getTeam() == caster.getTeam() and "crystal" in entity.getName():
                    continue
                if entity.getCell() is not None and entity.getTeam() == caster.getTeam():
                    cells.append(entity.getCell())
        return cells
