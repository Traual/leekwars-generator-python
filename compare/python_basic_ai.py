"""Python equivalent of test/ai/basic.leek (with library.leek inlined).

```leekscript
include("subfolder/library.leek")     // -> say("Library !");

var enemy = getNearestEnemy();
debug("w:" + getWeapons());
if (count(getWeapons())) {
    setWeapon(getWeapons()[0]);
}
moveToward(enemy);
useWeapon(enemy);
```
"""

from leekwars.classes import fight_class, entity_class, weapon_class


def basic_ai(ai):
    # include("subfolder/library.leek") -> say("Library !");
    entity_class.say(ai, "Library !")

    enemy = fight_class.getNearestEnemy(ai)

    weapons = entity_class.getWeapons(ai)
    # debug("w:" + getWeapons());  -> we add a normal log (matches LeekLog STANDARD path)
    ai.getLogs().addLog(0, "w:" + str(weapons))

    if weapons and len(weapons) > 0:
        entity_class.setWeapon(ai, weapons[0])

    fight_class.moveToward(ai, enemy)
    weapon_class.useWeapon(ai, enemy)
