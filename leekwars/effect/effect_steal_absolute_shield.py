from .effect import Effect


class EffectStealAbsoluteShield(Effect):

    def apply(self, state):
        from ..state.entity import Entity
        self.value = self.previousEffectTotalValue
        if self.value > 0:
            self.stats.setStat(Entity.STAT_ABSOLUTE_SHIELD, self.value)
            self.target.updateBuffStats(Entity.STAT_ABSOLUTE_SHIELD, self.value, self.caster)
