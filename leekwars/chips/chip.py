from ..items.item import Item
from ..attack.attack import Attack


class Chip(Item):

    def __init__(self, id, cost, minRange, maxRange, effects, launchType, area, los, cooldown, teamCooldown, initialCooldown, level, template, name, chipType, maxUses):
        super().__init__(id, cost, name, template,
                         Attack(minRange, maxRange, launchType, area, los, effects, Attack.TYPE_CHIP, id, maxUses))
        self.attack.setItem(self)

        self.cooldown = cooldown
        self.teamCooldown = teamCooldown
        self.initialCooldown = initialCooldown
        self.level = level
        self.chipType = chipType

    def getCooldown(self) -> int:
        return self.cooldown

    def isTeamCooldown(self) -> bool:
        return self.teamCooldown

    def getInitialCooldown(self) -> int:
        return self.initialCooldown

    def getLevel(self) -> int:
        return self.level

    def getChipType(self):
        return self.chipType

    def __str__(self) -> str:
        return self.name
