"""Python port of FightClass - movement and querying helpers.

Adapted from Java FightClass. Removes LeekScript value wrappers; functions
operate on Python ints / lists directly. Each function takes the EntityAI
as first argument, mirroring the Java signatures.
"""

from ..maps.map import Map
from ..maps.cell import Cell
from ..weapons import weapons as Weapons
from ..chips import chips as Chips
from ..bulbs import bulbs as Bulbs
from ..effect.effect import Effect
from ..fight.fight import Fight
from ..state.entity import Entity


def getNearestEnemy(ai) -> int:
    if ai.getEntity().getCell() is None:
        return -1
    entities = ai.getState().getEnemiesEntities(ai.getEntity().getTeam())
    dist = -1
    nearest = None
    for l in entities:
        if l.isDead() or l.getCell() is None:
            continue
        d = Map.getDistance2(ai.getEntity().getCell(), l.getCell())
        if d < dist or dist == -1:
            dist = d
            nearest = l
    return -1 if nearest is None else nearest.getFId()


def getFarestEnemy(ai) -> int:
    if ai.getEntity().getCell() is None:
        return -1
    entities = ai.getState().getEnemiesEntities(ai.getEntity().getTeam())
    dist = -1
    farest = None
    for l in entities:
        if l.isDead() or l.getCell() is None:
            continue
        d = Map.getDistance2(ai.getEntity().getCell(), l.getCell())
        if d > dist or dist == -1:
            dist = d
            farest = l
    return -1 if farest is None else farest.getFId()


def getFarthestEnemy(ai) -> int:
    return getFarestEnemy(ai)


def getTurn(ai) -> int:
    return ai.getFight().getTurn()


def getAllEffects(ai):
    return list(range(1, len(Effect.effects) + 1)) if Effect.effects else []


def getAliveEnemies(ai):
    result = []
    for e in ai.getState().getAllEntities(False):
        if e.getTeam() != ai.getEntity().getTeam():
            result.append(e.getFId())
    return result


def getAliveEnemiesCount(ai) -> int:
    count = 0
    for e in ai.getState().getAllEntities(False):
        if e.getTeam() != ai.getEntity().getTeam():
            count += 1
    return count


def getDeadEnemies(ai):
    result = []
    for e in ai.getState().getAllEntities(True):
        if e.getTeam() != ai.getEntity().getTeam() and e.isDead():
            result.append(e.getFId())
    return result


def getDeadEnemiesCount(ai) -> int:
    count = 0
    for e in ai.getState().getAllEntities(True):
        if e.getTeam() != ai.getEntity().getTeam() and e.isDead():
            count += 1
    return count


def getEnemies(ai):
    result = []
    for e in ai.getState().getEnemiesEntities(ai.getEntity().getTeam(), True):
        result.append(e.getFId())
    return result


def getEnemiesLife(ai) -> int:
    life = 0
    for e in ai.getState().getEnemiesEntities(ai.getEntity().getTeam()):
        life += e.getLife()
    return life


def getEnemiesCount(ai) -> int:
    return len(ai.getState().getEnemiesEntities(ai.getEntity().getTeam(), True))


def getAlliedTurret(ai):
    if ai.getState().getType() == Fight.TYPE_TEAM:
        for e in ai.getState().getTeamEntities(ai.getEntity().getTeam(), True):
            if e.getType() == Entity.TYPE_TURRET:
                return e.getFId()
    return None


def getEnemyTurret(ai):
    if ai.getState().getType() == Fight.TYPE_TEAM:
        for e in ai.getState().getEnemiesEntities(ai.getEntity().getTeam(), True):
            if e.getType() == Entity.TYPE_TURRET:
                return e.getFId()
    return None


def getNearestAlly(ai) -> int:
    if ai.getEntity().getCell() is None:
        return -1
    entities = ai.getState().getTeamEntities(ai.getEntity().getTeam())
    dist = -1
    nearest = None
    for l in entities:
        if l.isDead() or l is ai.getEntity() or l.getCell() is None:
            continue
        d = Map.getDistance2(ai.getEntity().getCell(), l.getCell())
        if d < dist or dist == -1:
            dist = d
            nearest = l
    return -1 if nearest is None else nearest.getFId()


def getFarestAlly(ai) -> int:
    if ai.getEntity().getCell() is None:
        return -1
    entities = ai.getState().getTeamEntities(ai.getEntity().getTeam())
    dist = -1
    farest = None
    for l in entities:
        if l.isDead() or l is ai.getEntity() or l.getCell() is None:
            continue
        d = Map.getDistance2(ai.getEntity().getCell(), l.getCell())
        if d > dist or dist == -1:
            dist = d
            farest = l
    return -1 if farest is None else farest.getFId()


def getFarthestAlly(ai) -> int:
    return getFarestAlly(ai)


def getAliveAllies(ai):
    retour = []
    for l in ai.getState().getTeamEntities(ai.getEntity().getTeam()):
        retour.append(l.getFId())
    return retour


def getAliveAlliesCount(ai) -> int:
    return len(ai.getState().getTeamEntities(ai.getEntity().getTeam()))


def getDeadAllies(ai):
    retour = []
    for l in ai.getState().getTeamEntities(ai.getEntity().getTeam(), True):
        if l.isDead():
            retour.append(l.getFId())
    return retour


def getDeadAlliesCount(ai) -> int:
    nb = 0
    for l in ai.getState().getTeamEntities(ai.getEntity().getTeam(), True):
        if l.isDead():
            nb += 1
    return nb


def getAllies(ai):
    retour = []
    for l in ai.getState().getTeamEntities(ai.getEntity().getTeam(), True):
        retour.append(l.getFId())
    return retour


def getAlliesCount(ai) -> int:
    return len(ai.getState().getTeamEntities(ai.getEntity().getTeam(), True))


def getAlliesLife(ai) -> int:
    life = 0
    for l in ai.getState().getTeamEntities(ai.getEntity().getTeam()):
        life += l.getLife()
    return life


def getNextPlayer(ai, value=None):
    if value is None:
        return ai.getFight().getOrder().getNextPlayer().getFId()
    entity = ai.getFight().getEntity(int(value))
    if entity is not None:
        next_ = ai.getFight().getOrder().getNextPlayer(entity)
        if next_ is not None:
            return next_.getFId()
    return None


def getPreviousPlayer(ai, value=None):
    if value is None:
        return ai.getFight().getOrder().getPreviousPlayer().getFId()
    entity = ai.getFight().getEntity(int(value))
    if entity is not None:
        prev = ai.getFight().getOrder().getPreviousPlayer(entity)
        if prev is not None:
            return prev.getFId()
    return None


def _put_cells(ai, ignore_list, cells_to_ignore):
    """Helper: convert ignore arg to cell list."""
    if cells_to_ignore is None:
        ignore_list.append(ai.getEntity().getCell())
        return
    for value in cells_to_ignore:
        l = ai.getState().getMap().getCell(int(value))
        if l is not None:
            ignore_list.append(l)


def getCellToUseWeapon(ai, value1, value2=None, value3=None) -> int:
    weapon = ai.getEntity().getWeapon()
    target = None

    if value2 is None:
        target = ai.getFight().getEntity(int(value1))
    else:
        weapon = Weapons.getWeapon(int(value1))
        target = ai.getFight().getEntity(int(value2))

    cell = -1
    if target is not None and target.getCell() is not None and weapon is not None:
        cells_to_ignore = []
        _put_cells(ai, cells_to_ignore, value3)
        possible = ai.getState().getMap().getPossibleCastCellsForTarget(weapon.getAttack(), target.getCell(), cells_to_ignore)
        if possible is not None and len(possible) > 0:
            if ai.getEntity().getCell() in possible:
                cell = ai.getEntity().getCell().getId()
            else:
                path = ai.getState().getMap().getAStarPath(ai.getEntity().getCell(), possible, cells_to_ignore)
                if path is not None:
                    if len(path) > 0:
                        cell = path[len(path) - 1].getId()
                    else:
                        cell = -1
    return cell


def getCellToUseWeaponOnCell(ai, value1, value2=None, value3=None) -> int:
    target = None
    weapon = ai.getEntity().getWeapon()

    if value2 is None:
        target = ai.getState().getMap().getCell(int(value1))
    else:
        weapon = Weapons.getWeapon(int(value1))
        target = ai.getState().getMap().getCell(int(value2))

    retour = -1
    if target is not None and weapon is not None:
        cells_to_ignore = []
        _put_cells(ai, cells_to_ignore, value3)
        possible = ai.getState().getMap().getPossibleCastCellsForTarget(weapon.getAttack(), target, cells_to_ignore)
        if possible is not None and len(possible) > 0:
            if ai.getEntity().getCell() in possible:
                retour = ai.getEntity().getCell().getId()
            else:
                path = ai.getState().getMap().getAStarPath(ai.getEntity().getCell(), possible, cells_to_ignore)
                if path is not None:
                    if len(path) > 0:
                        retour = path[len(path) - 1].getId()
                    else:
                        retour = -1
    return retour


def getCellToUseChip(ai, chip, t, value3=None) -> int:
    target = ai.getFight().getEntity(int(t))
    cell = -1
    if target is None:
        return cell
    template = Chips.getChip(int(chip))
    if template is None:
        return cell
    cells_to_ignore = []
    _put_cells(ai, cells_to_ignore, value3)
    possible = ai.getState().getMap().getPossibleCastCellsForTarget(template.getAttack(), target.getCell(), cells_to_ignore)
    if possible is not None and len(possible) > 0:
        if ai.getEntity().getCell() in possible:
            cell = ai.getEntity().getCell().getId()
        else:
            path = ai.getState().getMap().getAStarPath(ai.getEntity().getCell(), possible, cells_to_ignore)
            if path is not None:
                if len(path) > 0:
                    cell = path[len(path) - 1].getId()
                else:
                    cell = ai.getEntity().getCell().getId()
    return cell


def getCellToUseChipOnCell(ai, chip, cell, value3=None) -> int:
    retour = -1
    target = ai.getState().getMap().getCell(int(cell))
    if target is None:
        return int(cell)
    template = Chips.getChip(int(chip))
    if template is None:
        return int(cell)
    cells_to_ignore = []
    _put_cells(ai, cells_to_ignore, value3)
    possible = ai.getState().getMap().getPossibleCastCellsForTarget(template.getAttack(), target, cells_to_ignore)
    if possible is not None and len(possible) > 0:
        if ai.getEntity().getCell() in possible:
            retour = ai.getEntity().getCell().getId()
        else:
            path = ai.getState().getMap().getAStarPath(ai.getEntity().getCell(), possible)
            if path is not None:
                if len(path) > 0:
                    retour = path[len(path) - 1].getId()
                else:
                    retour = ai.getEntity().getCell().getId()
    return retour


def moveToward(ai, leek_id, pm_to_use=-1) -> int:
    return ai.getState().moveToward(ai.getEntity(), leek_id, pm_to_use)


def moveTowardCell(ai, cell_id, pm_to_use=None) -> int:
    if pm_to_use is None:
        pm_to_use = ai.getEntity().getMP()
    return ai.getState().moveTowardCell(ai.getEntity(), cell_id, pm_to_use)


def moveTowardLeeks(ai, leeks, pm_to_use=-1) -> int:
    pm = ai.getEntity().getMP() if pm_to_use == -1 else int(pm_to_use)
    if pm > ai.getEntity().getMP():
        pm = ai.getEntity().getMP()
    used_pm = 0
    if pm > 0:
        targets = []
        for value in leeks:
            l = ai.getFight().getEntity(int(value))
            if l is not None and not l.isDead():
                targets.append(l.getCell())
        if len(targets) != 0:
            path = ai.getState().getMap().getAStarPath(ai.getEntity().getCell(), targets)
            if path is not None:
                used_pm = ai.getState().moveEntity(ai.getEntity(), path[:min(pm, len(path))])
    return used_pm


def moveTowardCells(ai, cells, pm_to_use=-1) -> int:
    pm = ai.getEntity().getMP() if pm_to_use == -1 else int(pm_to_use)
    if pm > ai.getEntity().getMP():
        pm = ai.getEntity().getMP()
    used_pm = 0
    if pm > 0:
        targets = []
        for value in cells:
            c = ai.getState().getMap().getCell(int(value))
            if c is not None:
                targets.append(c)
        if len(targets) != 0:
            path = ai.getState().getMap().getAStarPath(ai.getEntity().getCell(), targets)
            if path is not None:
                used_pm = ai.getState().moveEntity(ai.getEntity(), path[:min(pm, len(path))])
    return used_pm


def moveAwayFrom(ai, leek_id, pm_to_use=-1) -> int:
    pm = ai.getEntity().getMP() if pm_to_use == -1 else int(pm_to_use)
    if pm > ai.getEntity().getMP():
        pm = ai.getEntity().getMP()
    used_pm = 0
    if pm > 0:
        target = ai.getFight().getEntity(leek_id)
        if target is not None and target.getCell() is not None:
            cells = [target.getCell()]
            path = ai.getState().getMap().getPathAway(ai.getEntity().getCell(), cells, pm)
            if path is not None:
                used_pm = ai.getState().moveEntity(ai.getEntity(), path)
    return used_pm


def moveAwayFromCell(ai, cell_id, pm_to_use=-1) -> int:
    pm = ai.getEntity().getMP() if pm_to_use == -1 else int(pm_to_use)
    if pm > ai.getEntity().getMP():
        pm = ai.getEntity().getMP()
    used_pm = 0
    if pm > 0:
        target = ai.getState().getMap().getCell(int(cell_id))
        if target is not None:
            cells = [target]
            path = ai.getState().getMap().getPathAway(ai.getEntity().getCell(), cells, pm)
            if path is not None:
                used_pm = ai.getState().moveEntity(ai.getEntity(), path)
    return used_pm


def getEntityTurnOrder(ai, value=None):
    if value is None:
        return ai.getFight().getOrder().getEntityTurnOrder(ai.getEntity())
    l = ai.getFight().getEntity(int(value))
    if l is not None and not l.isDead():
        return ai.getFight().getOrder().getEntityTurnOrder(l)
    return None


def getNearestEnemyTo(ai, leek_id):
    entities = ai.getState().getEnemiesEntities(ai.getEntity().getTeam())
    entity = ai.getFight().getEntity(leek_id)
    if entity is None or entity.getCell() is None:
        return None
    dist = -1
    nearest = None
    for l in entities:
        if l.isDead():
            continue
        if entity is l:
            continue
        if l.getCell() is None:
            continue
        d = Map.getDistance2(entity.getCell(), l.getCell())
        if d < dist or dist == -1:
            dist = d
            nearest = l
    return None if nearest is None else nearest.getFId()


def getNearestEnemyToCell(ai, cell_id):
    entities = ai.getState().getEnemiesEntities(ai.getEntity().getTeam())
    cell = ai.getState().getMap().getCell(int(cell_id))
    if cell is None:
        return None
    dist = -1
    nearest = None
    for l in entities:
        if l.isDead() or l.getCell() is None:
            continue
        d = Map.getDistance2(cell, l.getCell())
        if d < dist or dist == -1:
            dist = d
            nearest = l
    return None if nearest is None else nearest.getFId()


def getNearestAllyTo(ai, leek_id):
    entities = ai.getState().getTeamEntities(ai.getEntity().getTeam())
    entity = ai.getFight().getEntity(leek_id)
    if entity is None or entity.getCell() is None:
        return None
    dist = -1
    nearest = None
    for l in entities:
        if l.isDead():
            continue
        if entity is l or l is ai.getEntity():
            continue
        d = Map.getDistance2(entity.getCell(), l.getCell())
        if d < dist or dist == -1:
            dist = d
            nearest = l
    return None if nearest is None else nearest.getFId()


def getNearestAllyToCell(ai, cell_id):
    entities = ai.getState().getTeamEntities(ai.getEntity().getTeam())
    cell = ai.getState().getMap().getCell(int(cell_id))
    if cell is None:
        return None
    dist = -1
    nearest = None
    for l in entities:
        if l.isDead():
            continue
        if l is ai.getEntity():
            continue
        d = Map.getDistance2(cell, l.getCell())
        if d < dist or dist == -1:
            dist = d
            nearest = l
    return None if nearest is None else nearest.getFId()


def getFightType(ai) -> int:
    return ai.getState().getType()


def getFightContext(ai) -> int:
    return ai.getState().getContext()


def getFightID(ai) -> int:
    return ai.getFight().getId()


def getFightBoss(ai) -> int:
    return ai.getFight().getBoss()
