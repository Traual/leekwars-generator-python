TYPE_WEAPON = 1
TYPE_CHIP = 2
TYPE_POTION = 3
TYPE_COMPONENT = 8


_items = {}


def addWeapon(id_: int) -> None:
    _items[id_] = TYPE_WEAPON


def addChip(id_: int) -> None:
    _items[id_] = TYPE_CHIP


def addComponent(id_: int) -> None:
    _items[id_] = TYPE_COMPONENT


def getType(item: int):
    return _items.get(item)
