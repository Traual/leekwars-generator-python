import math

from .effect import Effect
from ..util.java_math import java_round
from ..state.entity import Entity


class EffectMultiplyStats(Effect):
    """Multiplies all stats of the target by value1.
    Used for Colossus mode to boost the colossus's stats."""

    def apply(self, state):

        factor = int(self.value1)
        if factor <= 1:
            return

        self.value = factor

        # Multiply all base stats (except life, handled separately)
        statIds = [
            Entity.STAT_STRENGTH, Entity.STAT_AGILITY,
            Entity.STAT_RESISTANCE, Entity.STAT_WISDOM, Entity.STAT_SCIENCE,
            Entity.STAT_MAGIC, Entity.STAT_FREQUENCY, Entity.STAT_TP, Entity.STAT_MP
        ]

        for statId in statIds:
            base = self.target.getBaseStats().getStat(statId)
            buff = base * (factor - 1)
            if buff > 0:
                self.stats.setStat(statId, buff)
                self.target.updateBuffStats(statId, buff, self.caster)

        lifeBase = self.target.getBaseStats().getStat(Entity.STAT_LIFE)
        if self.target.getTotalLife() <= lifeBase:
            # First apply: no previous boost
            lifeDelta = lifeBase * (factor - 1)
        else:
            # Replacement: previous boost still in mTotalLife, just add 1x base
            lifeDelta = lifeBase

        ratio = (self.target.getLife() / self.target.getTotalLife()) if self.target.getTotalLife() > 0 else 1.0
        self.target.addTotalLife(lifeDelta, self.caster)
        targetLife = java_round(self.target.getTotalLife() * ratio)
        healAmount = targetLife - self.target.getLife()
        if healAmount > 0:
            self.target.addLife(self.caster, healAmount)
