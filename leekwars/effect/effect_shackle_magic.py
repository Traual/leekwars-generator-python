import math

from .effect import Effect
from ..util.java_math import java_round
from ..state.entity import Entity


class EffectShackleMagic(Effect):

    def apply(self, fight):
        # Base shackle : base × (1 + magic / 100)
        self.value = java_round((self.value1 + self.jet * self.value2) * (1.0 + max(0, self.caster.getMagic()) / 100.0) * self.aoe * self.criticalPower)
        if self.value > 0:
            self.stats.setStat(Entity.STAT_MAGIC, -self.value)
            self.target.updateBuffStats(Entity.STAT_MAGIC, -self.value, self.caster)
