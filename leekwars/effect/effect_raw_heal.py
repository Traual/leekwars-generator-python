import math

from .effect import Effect
from ..action.action_heal import ActionHeal
from ..attack.entity_state import EntityState


class EffectRawHeal(Effect):

    def apply(self, state):

        if self.target.hasState(EntityState.UNHEALABLE):
            return

        self.value = java_round((self.value1 + self.jet * self.value2) * self.aoe * self.criticalPower * self.targetCount)

        if self.target.getLife() + self.value > self.target.getTotalLife():
            self.value = self.target.getTotalLife() - self.target.getLife()
        state.log(ActionHeal(self.target, self.value))
        self.target.addLife(self.caster, self.value)
