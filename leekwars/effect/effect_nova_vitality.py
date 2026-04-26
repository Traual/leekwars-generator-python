import math

from .effect import Effect
from ..action.action_nova_vitality import ActionNovaVitality


class EffectNovaVitality(Effect):

    def apply(self, state):
        self.value = java_round((self.value1 + self.jet * self.value2) * (1 + self.caster.getScience() / 100.0) * self.aoe * self.criticalPower)

        state.log(ActionNovaVitality(self.target, self.value))
        self.target.addTotalLife(self.value, self.caster)
