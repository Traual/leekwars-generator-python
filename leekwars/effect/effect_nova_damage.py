import math

from .effect import Effect
from ..action.action_damage import ActionDamage
from ..attack.damage_type import DamageType
from ..attack.entity_state import EntityState
from ..util.java_math import java_round


class EffectNovaDamage(Effect):

    def apply(self, state):
        # Base damages
        d = (self.value1 + self.jet * self.value2) * (1 + max(0, self.caster.getScience()) / 100.0) * self.aoe * self.criticalPower * (1 + self.caster.getPower() / 100.0)

        if self.target.hasState(EntityState.INVINCIBLE):
            d = 0

        self.value = java_round(d)

        if self.value > self.target.getTotalLife() - self.target.getLife():
            self.value = self.target.getTotalLife() - self.target.getLife()

        state.log(ActionDamage(DamageType.NOVA, self.target, self.value, 0))
        self.target.removeLife(0, self.value, self.caster, DamageType.NOVA, self, self.getItem())
        self.target.onNovaDamage(self.value)
