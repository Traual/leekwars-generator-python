"""Sample AI - replicates the logic of test/ai/basic.leek.

A Python AI is just a function that takes an EntityAI instance and uses
the provided helpers (FightClass, EntityClass, WeaponClass, ChipClass)
to drive the entity.
"""

from leekwars.classes import fight_class, entity_class, weapon_class


def basic_ai(ai):
    enemy = fight_class.getNearestEnemy(ai)

    weapons = entity_class.getWeapons(ai)
    if weapons and len(weapons) > 0:
        entity_class.setWeapon(ai, weapons[0])

    fight_class.moveToward(ai, enemy)

    if enemy >= 0:
        weapon_class.useWeapon(ai, enemy)
