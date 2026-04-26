import math

from .effect import Effect


class EffectRawBuffMP(Effect):

    def apply(self, state):
        from ..state.entity import Entity
        self.value = java_round((self.value1 + self.value2 * self.jet) * self.targetCount * self.criticalPower)
        if self.value > 0:
            self.stats.setStat(Entity.STAT_MP, self.value)
            self.target.updateBuffStats(Entity.STAT_MP, self.value, self.caster)
