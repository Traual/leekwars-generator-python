import math

from .effect import Effect
from ..action.action_damage import ActionDamage
from ..attack.damage_type import DamageType
from ..attack.entity_state import EntityState


class EffectAftereffect(Effect):

    def apply(self, state):
        self.value = java_round((self.value1 + self.value2 * self.jet) * (1 + self.caster.getScience() / 100.0) * self.aoe * self.criticalPower)
        self.value = max(0, self.value)

        if self.target.hasState(EntityState.INVINCIBLE):
            self.value = 0

        if self.target.getLife() < self.value:
            self.value = self.target.getLife()
        erosion = java_round(self.value * self.erosionRate)

        state.log(ActionDamage(DamageType.AFTEREFFECT, self.target, self.value, erosion))
        self.target.removeLife(self.value, erosion, self.caster, DamageType.AFTEREFFECT, self, self.getItem())
        self.target.onNovaDamage(erosion)

    def applyStartTurn(self, state):
        if self.target.getLife() < self.value:
            self.value = self.target.getLife()
        erosion = java_round(self.value * self.erosionRate)

        state.log(ActionDamage(DamageType.AFTEREFFECT, self.target, self.value, erosion))
        self.target.removeLife(self.value, erosion, self.caster, DamageType.AFTEREFFECT, self, self.getItem())
        self.target.onNovaDamage(erosion)
