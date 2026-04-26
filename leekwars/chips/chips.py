from ..items import items as Items


_chips = {}


def addChip(chip) -> None:
    _chips[chip.getId()] = chip
    Items.addChip(chip.getId())


def getChip(id_or_name):
    if isinstance(id_or_name, str):
        for c in _chips.values():
            if c.getName() == id_or_name:
                return c
        return None
    return _chips.get(id_or_name)


def getTemplates():
    return _chips
