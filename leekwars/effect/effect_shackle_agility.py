import math

from .effect import Effect


class EffectShackleAgility(Effect):

    def apply(self, state):
        from ..state.entity import Entity
        # Base shackle : base × (1 + magic / 100)
        self.value = java_round((self.value1 + self.jet * self.value2) * (1.0 + max(0, self.caster.getMagic()) / 100.0) * self.aoe * self.criticalPower)
        if self.value > 0:
            self.stats.setStat(Entity.STAT_AGILITY, -self.value)
            self.target.updateBuffStats(Entity.STAT_AGILITY, -self.value, self.caster)
