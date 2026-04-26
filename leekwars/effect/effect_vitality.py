import math

from .effect import Effect
from ..action.action_vitality import ActionVitality


class EffectVitality(Effect):

    def apply(self, state):
        self.value = java_round((self.value1 + self.jet * self.value2) * (1 + self.caster.getWisdom() / 100.0) * self.aoe * self.criticalPower)

        self.value = max(0, self.value)  # Soin negatif si la sagesse est negative

        state.log(ActionVitality(self.target, self.value))
        self.target.addTotalLife(self.value, self.caster)
        self.target.addLife(self.caster, self.value)
