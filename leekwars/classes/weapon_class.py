"""Python port of WeaponClass."""

from ..attack.attack import Attack
from ..items import items as Items
from ..weapons import weapons as Weapons


def useWeapon(ai, leek_id) -> int:
    success = -1
    target = ai.getFight().getEntity(leek_id)
    if target is not None and target is not ai.getEntity() and not target.isDead():
        success = ai.getState().useWeapon(ai.getEntity(), target.getCell())
    if ai.getEntity().isDead():
        raise Exception("ENTITY_DIED")
    return success


def useWeaponOnCell(ai, cell_id) -> int:
    success = -1
    target = ai.getState().getMap().getCell(int(cell_id))
    if target is not None and target is not ai.getEntity().getCell():
        success = ai.getState().useWeapon(ai.getEntity(), target)
    if ai.getEntity().isDead():
        raise Exception("ENTITY_DIED")
    return success


def _get_weapon(ai, id_):
    if id_ is None or id_ == -1:
        return ai.getEntity().getWeapon()
    return Weapons.getWeapon(int(id_))


def getWeaponMinScope(ai, id_=None) -> int:
    template = _get_weapon(ai, id_)
    if template is None:
        return -1
    return template.getAttack().getMinRange()


def getWeaponMinRange(ai, id_=None) -> int:
    return getWeaponMinScope(ai, id_)


def getWeaponFailure(ai, id_=None) -> int:
    return 0


def getWeaponMaxScope(ai, id_=None) -> int:
    template = _get_weapon(ai, id_)
    if template is None:
        return -1
    return template.getAttack().getMaxRange()


def getWeaponMaxRange(ai, id_=None) -> int:
    return getWeaponMaxScope(ai, id_)


def getWeaponCost(ai, id_=None) -> int:
    template = _get_weapon(ai, id_)
    if template is None:
        return -1
    return template.getCost()


def isInlineWeapon(ai, id_=None) -> bool:
    template = _get_weapon(ai, id_)
    if template is None:
        return False
    return template.getAttack().getLaunchType() == Attack.LAUNCH_TYPE_LINE


def getWeaponName(ai, id_=None) -> str:
    template = _get_weapon(ai, id_)
    if template is None:
        return ""
    return template.getName()


def _featureToList(feature):
    return [feature.getId(), feature.getValue1(), feature.getValue1() + feature.getValue2(),
            feature.getTurns(), feature.getTargets(), feature.getModifiers()]


def getWeaponEffects(ai, id_=None):
    template = _get_weapon(ai, id_)
    if template is None:
        return None
    return [_featureToList(f) for f in template.getAttack().getEffects()]


def getWeaponPassiveEffects(ai, id_=None):
    template = _get_weapon(ai, id_)
    if template is None:
        return None
    return [_featureToList(f) for f in template.getPassiveEffects()]


def getWeaponLaunchType(ai, weapon_id=None):
    template = _get_weapon(ai, weapon_id)
    if template is None:
        return None
    return template.getAttack().getLaunchType()


def weaponNeedLos(ai, id_=None) -> bool:
    template = _get_weapon(ai, id_)
    if template is None:
        return False
    return template.getAttack().needLos()


def canUseWeapon(ai, value1, value2=None) -> bool:
    if value2 is None:
        target = ai.getFight().getEntity(int(value1))
        weapon = ai.getEntity().getWeapon()
    else:
        target = ai.getFight().getEntity(int(value2))
        weapon = Weapons.getWeapon(int(value1))
    if weapon is None:
        return False
    if target is not None and target.getCell() is not None:
        return ai.getState().getMap().canUseAttack(ai.getEntity().getCell(), target.getCell(), weapon.getAttack())
    return False


def canUseWeaponOnCell(ai, value1, value2=None) -> bool:
    if value2 is None:
        target = ai.getState().getMap().getCell(int(value1))
        weapon = ai.getEntity().getWeapon()
    else:
        target = ai.getState().getMap().getCell(int(value2))
        weapon = Weapons.getWeapon(int(value1))
    if weapon is None:
        return False
    if target is not None:
        return ai.getState().getMap().canUseAttack(ai.getEntity().getCell(), target, weapon.getAttack())
    return False


def getWeaponTargets(ai, value1, value2=None):
    if value2 is None:
        target = ai.getState().getMap().getCell(int(value1))
        weapon = ai.getEntity().getWeapon()
    else:
        weapon = Weapons.getWeapon(int(value1))
        target = ai.getState().getMap().getCell(int(value2))

    if weapon is None:
        return None
    if target is not None and ai.getEntity().getCell() is not None:
        leeks = weapon.getAttack().getWeaponTargets(ai.getState(), ai.getEntity(), target)
        return [l.getFId() for l in leeks]
    return None


def getWeaponEffectiveArea(ai, value1, value2=None, value3=None):
    if value2 is None:
        target = ai.getState().getMap().getCell(int(value1))
        weapon = ai.getEntity().getWeapon()
    else:
        weapon = Weapons.getWeapon(int(value1))
        target = ai.getState().getMap().getCell(int(value2))

    start_cell = ai.getEntity().getCell()
    if value3 is not None:
        start_cell = ai.getState().getMap().getCell(int(value3))

    if target is None or weapon is None or start_cell is None:
        return None

    cells = weapon.getAttack().getTargetCells(ai.getState().getMap(), start_cell, target)
    return [c.getId() for c in cells]


def isWeapon(ai, id_) -> bool:
    i = Items.getType(int(id_))
    if i is None:
        return False
    return i == Items.TYPE_WEAPON


def getWeaponArea(ai, value):
    weapon = Weapons.getWeapon(int(value))
    if weapon is not None:
        return weapon.getAttack().getArea()
    return None


def getAllWeapons(ai):
    return [w.getId() for w in Weapons.getTemplates().values()]


def getWeaponMaxUses(ai, id_=None) -> int:
    template = _get_weapon(ai, id_)
    if template is None:
        return -1
    return template.getAttack().getMaxUses()
