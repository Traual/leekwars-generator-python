import math

from .effect import Effect
from ..action.action_damage import ActionDamage
from ..attack.damage_type import DamageType
from ..attack.entity_state import EntityState
from ..util.java_math import java_round


class EffectPoison(Effect):

    def apply(self, state):
        self.value = java_round((self.value1 + self.jet * self.value2) * (1 + max(0, self.caster.getMagic()) / 100.0) * self.aoe * self.criticalPower * (1 + self.caster.getPower() / 100.0))

    def applyStartTurn(self, state):
        damages = self.value
        if self.target.getLife() < damages:
            damages = self.target.getLife()

        if self.target.hasState(EntityState.INVINCIBLE):
            damages = 0

        if damages > 0:
            erosion = java_round(damages * self.erosionRate)

            state.log(ActionDamage(DamageType.POISON, self.target, damages, erosion))
            self.target.removeLife(damages, erosion, self.caster, DamageType.POISON, self, self.getItem())
            self.target.onPoisonDamage(damages)
            self.target.onNovaDamage(erosion)
