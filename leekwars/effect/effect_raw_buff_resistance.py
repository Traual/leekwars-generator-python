import math

from .effect import Effect


class EffectRawBuffResistance(Effect):

    def apply(self, state):
        from ..state.entity import Entity
        self.value = java_round((self.value1 + self.jet * self.value2) * self.aoe * self.criticalPower)
        if self.value > 0:
            self.stats.setStat(Entity.STAT_RESISTANCE, self.value)
            self.target.updateBuffStats(Entity.STAT_RESISTANCE, self.value, self.caster)
