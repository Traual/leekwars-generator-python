"""Python port of ChipClass."""

from ..attack.attack import Attack
from ..chips import chips as Chips
from ..items import items as Items


def getCooldown(ai, chip_id, v=None):
    if v is None:
        chipTemplate = Chips.getChip(int(chip_id))
        return ai.getState().getCooldown(ai.getEntity(), chipTemplate)
    l = ai.getFight().getEntity(int(v))
    if l is not None:
        chipTemplate = Chips.getChip(int(chip_id))
        return ai.getState().getCooldown(l, chipTemplate)
    return None


def useChip(ai, chip_id, leek_id=None) -> int:
    if leek_id is None:
        leek_id = ai.getEntity().getFId()
    success = -1
    target = ai.getFight().getEntity(leek_id)
    chip = ai.getEntity().getChip(int(chip_id))
    if target is not None and chip is not None and not target.isDead():
        success = ai.getFight().useChip(ai.getEntity(), target.getCell(), chip)
    if ai.getEntity().isDead():
        raise Exception("ENTITY_DIED")
    return success


def useChipOnCell(ai, chip_id, cell_id) -> int:
    success = -1
    target = ai.getState().getMap().getCell(int(cell_id))
    template = ai.getEntity().getChip(int(chip_id))
    if target is not None and template is not None:
        success = ai.getFight().useChip(ai.getEntity(), target, template)
    if ai.getEntity().isDead():
        raise Exception("ENTITY_DIED")
    return success


def canUseChipOnCell(ai, chip_id, cell_id) -> bool:
    target = ai.getState().getMap().getCell(int(cell_id))
    template = ai.getEntity().getChip(int(chip_id))
    if target is not None and template is not None and ai.getEntity().getCell() is not None:
        return ai.getState().getMap().canUseAttack(ai.getEntity().getCell(), target, template.getAttack())
    return False


def canUseChip(ai, chip_id, leek_id) -> bool:
    target = ai.getFight().getEntity(int(leek_id))
    template = ai.getEntity().getChip(int(chip_id))
    if target is not None and template is not None and target.getCell() is not None and ai.getEntity().getCell() is not None:
        return ai.getState().getMap().canUseAttack(ai.getEntity().getCell(), target.getCell(), template.getAttack())
    return False


def getChipTargets(ai, chip_id, cell_id):
    target = ai.getState().getMap().getCell(int(cell_id))
    template = Chips.getChip(int(chip_id))
    if target is not None and template is not None:
        entities = template.getAttack().getWeaponTargets(ai.getState(), ai.getEntity(), ai.getState().getMap().getCell(int(cell_id)))
        return [l.getFId() for l in entities]
    return None


def getChipName(ai, id_) -> str:
    chip = Chips.getChip(int(id_))
    if chip is None:
        return ""
    return chip.getName()


def getChipCooldown(ai, id_) -> int:
    chip = Chips.getChip(int(id_))
    if chip is None:
        return 0
    return chip.getCooldown()


def getChipMinScope(ai, id_):
    chip = Chips.getChip(int(id_))
    if chip is None:
        return None
    return chip.getAttack().getMinRange()


def getChipMinRange(ai, id_):
    return getChipMinScope(ai, id_)


def getChipMaxScope(ai, id_):
    chip = Chips.getChip(int(id_))
    if chip is None:
        return None
    return chip.getAttack().getMaxRange()


def getChipMaxRange(ai, id_):
    return getChipMaxScope(ai, id_)


def getChipFailure(ai, id_) -> int:
    return 0


def getChipCost(ai, id_):
    chip = Chips.getChip(int(id_))
    if chip is None:
        return None
    return chip.getCost()


def isInlineChip(ai, id_) -> bool:
    chip = Chips.getChip(int(id_))
    if chip is None:
        return False
    return chip.getAttack().getLaunchType() == Attack.LAUNCH_TYPE_LINE


def _featureToList(feature):
    return [feature.getId(), feature.getValue1(), feature.getValue1() + feature.getValue2(),
            feature.getTurns(), feature.getTargets(), feature.getModifiers()]


def getChipEffects(ai, id_):
    chip = Chips.getChip(int(id_))
    if chip is None:
        return None
    return [_featureToList(f) for f in chip.getAttack().getEffects()]


def summon(ai, chip, cell, summonAI, name=None) -> int:
    success = -1
    target = ai.getState().getMap().getCell(int(cell))
    if target is None:
        return -1
    if summonAI is None:
        return -1
    template = ai.getEntity().getChip(int(chip))
    if template is None:
        return -1
    if target is not None and template is not None:
        success = ai.getFight().summonEntity(ai.getEntity(), target, template, summonAI, name)
    return success


def resurrect(ai, entity, cell) -> int:
    success = -1
    target = ai.getState().getMap().getCell(int(cell))
    if target is None:
        return -1
    l = ai.getFight().getEntity(int(entity))
    if l is None or not l.isDead():
        return -6  # USE_RESURRECT_INVALID_ENTITY
    template = ai.getEntity().getChip(84)  # CHIP_RESURRECTION
    template2 = ai.getEntity().getChip(415)
    fullLife = template2 is not None
    if template is None and template2 is None:
        return -1
    if target is not None and (template is not None or template2 is not None):
        success = ai.getState().resurrectEntity(ai.getEntity(), target, template if template is not None else template2, l, fullLife)
    return success


def getChipEffectiveArea(ai, value1, value2, value3=None):
    start_cell = ai.getEntity().getCell()
    if value3 is not None:
        start_cell = ai.getState().getMap().getCell(int(value3))
    if start_cell is None:
        return None
    c = ai.getState().getMap().getCell(int(value2))
    if c is None or ai.getEntity().getCell() is None:
        return None
    template = Chips.getChip(int(value1))
    if template is None:
        return None
    cells = template.getAttack().getTargetCells(ai.getState().getMap(), start_cell, c)
    if cells is None:
        return []
    return [cell.getId() for cell in cells]


def getAllChips(ai):
    return [c.getId() for c in Chips.getTemplates().values()]


def chipNeedLos(ai, id_) -> bool:
    chip = Chips.getChip(int(id_))
    if chip is None:
        return False
    return chip.getAttack().needLos()


def isChip(ai, id_) -> bool:
    i = Items.getType(int(id_))
    if i is None:
        return False
    return i == Items.TYPE_CHIP


def getChipLaunchType(ai, chip_id):
    template = Chips.getChip(int(chip_id))
    if template is None:
        return None
    return template.getAttack().getLaunchType()


def getChipArea(ai, value):
    template = Chips.getChip(int(value))
    if template is not None:
        return template.getAttack().getArea()
    return None


def getChipMaxUses(ai, value):
    template = Chips.getChip(int(value))
    if template is not None:
        return template.getAttack().getMaxUses()
    return None
