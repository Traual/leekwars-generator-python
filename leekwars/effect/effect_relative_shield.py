import math

from .effect import Effect


class EffectRelativeShield(Effect):

    def apply(self, state):
        from ..state.entity import Entity
        self.value = java_round((self.value1 + self.jet * self.value2) * (1 + self.caster.getResistance() / 100.0) * self.aoe * self.criticalPower)
        if self.value > 0:
            self.stats.setStat(Entity.STAT_RELATIVE_SHIELD, self.value)
            self.target.updateBuffStats(Entity.STAT_RELATIVE_SHIELD, self.value, self.caster)
