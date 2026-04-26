import math

from .effect import Effect


class EffectBuffTP(Effect):

    def apply(self, state):
        from ..state.entity import Entity

        self.value = java_round((self.value1 + self.value2 * self.jet) * (1 + self.caster.getScience() / 100.0) * self.aoe * self.criticalPower)
        if self.value > 0:
            self.stats.setStat(Entity.STAT_TP, self.value)
            self.target.updateBuffStats(Entity.STAT_TP, self.value, self.caster)
