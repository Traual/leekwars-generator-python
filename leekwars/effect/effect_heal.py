import math

from .effect import Effect
from ..action.action_heal import ActionHeal
from ..attack.entity_state import EntityState


class EffectHeal(Effect):

    def apply(self, state):
        self.value = java_round((self.value1 + self.jet * self.value2) * (1 + self.caster.getWisdom() / 100.0) * self.aoe * self.criticalPower * self.targetCount)

        self.value = max(0, self.value)  # Soin negatif si la sagesse est negative

        if self.turns == 0:

            if self.target.hasState(EntityState.UNHEALABLE):
                return

            if self.target.getLife() + self.value > self.target.getTotalLife():
                self.value = self.target.getTotalLife() - self.target.getLife()
            state.log(ActionHeal(self.target, self.value))
            self.target.addLife(self.caster, self.value)

    def applyStartTurn(self, state):

        if self.target.hasState(EntityState.UNHEALABLE):
            return

        life = self.value
        if self.target.getLife() + life > self.target.getTotalLife():
            life = self.target.getTotalLife() - self.target.getLife()
        state.log(ActionHeal(self.target, life))
        self.target.addLife(self.caster, life)
