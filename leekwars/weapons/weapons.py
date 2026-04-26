from ..items import items as Items


_weapons = {}


def addWeapon(weapon) -> None:
    _weapons[weapon.getId()] = weapon
    Items.addWeapon(weapon.getId())


def getWeapon(id_or_name):
    if isinstance(id_or_name, str):
        for w in _weapons.values():
            if w.getName() == id_or_name:
                return w
        return None
    return _weapons.get(id_or_name)


def getTemplates():
    return _weapons
