from .effect import Effect
from ..action.action_reduce_effects import ActionReduceEffects


class EffectDebuff(Effect):

    def apply(self, state):
        self.value = int((self.value1 + self.jet * self.value2) * self.aoe * self.criticalPower * self.targetCount)
        self.target.reduceEffects(self.value / 100.0, self.caster)

        # "Les effets de X sont réduits de Y%"
        state.log(ActionReduceEffects(self.target, self.value))
