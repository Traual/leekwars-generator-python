from .effect import Effect
from ..state.entity import Entity


class EffectStealAbsoluteShield(Effect):

    def apply(self, state):
        self.value = self.previousEffectTotalValue
        if self.value > 0:
            self.stats.setStat(Entity.STAT_ABSOLUTE_SHIELD, self.value)
            self.target.updateBuffStats(Entity.STAT_ABSOLUTE_SHIELD, self.value, self.caster)
