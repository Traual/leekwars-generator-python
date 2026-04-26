import math

from .effect import Effect
from ..util.java_math import java_round


class EffectRawBuffStrength(Effect):

    def apply(self, state):
        from ..state.entity import Entity
        self.value = java_round((self.value1 + self.jet * self.value2) * self.aoe * self.criticalPower)
        if self.value > 0:
            self.stats.setStat(Entity.STAT_STRENGTH, self.value)
            self.target.updateBuffStats(Entity.STAT_STRENGTH, self.value, self.caster)
