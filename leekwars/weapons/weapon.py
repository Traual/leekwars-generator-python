from ..items.item import Item
from ..effect.effect_parameters import EffectParameters
from ..attack.attack import Attack


class Weapon(Item):

    def __init__(self, id, cost, minRange, maxRange, effects, launchType, area, los, template, name, passiveEffects, maxUses):
        super().__init__(id, cost, name, template,
                         Attack(minRange, maxRange, launchType, area, los, effects, Attack.TYPE_WEAPON, id, maxUses))
        self.attack.setItem(self)

        self.passiveEffects = []
        for e in passiveEffects:
            etype = e["id"]
            value1 = e["value1"]
            value2 = e["value2"]
            turns = e["turns"]
            targets = e["targets"]
            modifiers = e["modifiers"]
            self.passiveEffects.append(EffectParameters(etype, value1, value2, turns, targets, modifiers))

    def getId(self) -> int:
        return self.id

    def getTemplate(self) -> int:
        return self.template

    def getCost(self) -> int:
        return self.cost

    def getAttack(self):
        return self.attack

    def getName(self) -> str:
        return self.name

    def getPassiveEffects(self):
        return self.passiveEffects

    def isHandToHandWeapon(self) -> bool:
        return self.attack.getMinRange() == 1 and self.attack.getMaxRange() == 1

    def __str__(self) -> str:
        return self.name
