import math

from .effect import Effect
from ..action.action_damage import ActionDamage
from ..attack.damage_type import DamageType
from ..attack.entity_state import EntityState
from ..util.java_math import java_round


class EffectLifeDamage(Effect):

    def __init__(self):
        super().__init__()
        self.returnDamage = 0

    def apply(self, state):
        # Base damages
        d = ((self.value1 + self.jet * self.value2) / 100.0) * self.caster.getLife() * self.aoe * self.criticalPower * (1 + self.caster.getPower() / 100.0)

        if self.target.hasState(EntityState.INVINCIBLE):
            d = 0

        # Return damage
        if self.target is not self.caster:
            self.returnDamage = java_round(d * self.target.getDamageReturn() / 100.0)

        # Shields
        d -= d * (self.target.getRelativeShield() / 100.0) + self.target.getAbsoluteShield()
        d = max(0, d)

        self.value = java_round(d)

        if self.target.getLife() < self.value:
            self.value = self.target.getLife()

        erosion = java_round(self.value * self.erosionRate)

        state.log(ActionDamage(DamageType.LIFE, self.target, self.value, erosion))
        self.target.removeLife(self.value, erosion, self.caster, DamageType.LIFE, self, self.getItem())
        self.target.onDirectDamage(self.value)
        self.target.onNovaDamage(erosion)

        # Return damage
        if self.returnDamage > 0 and not self.caster.hasState(EntityState.INVINCIBLE):

            if self.caster.getLife() < self.returnDamage:
                self.returnDamage = self.caster.getLife()

            returnErosion = java_round(self.returnDamage * self.erosionRate)

            if self.returnDamage > 0:
                state.log(ActionDamage(DamageType.RETURN, self.caster, self.returnDamage, returnErosion))
                self.caster.removeLife(self.returnDamage, returnErosion, self.target, DamageType.RETURN, self, self.getItem())
