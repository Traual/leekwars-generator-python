import math

from .effect import Effect
from ..action.action_damage import ActionDamage
from ..action.action_heal import ActionHeal
from ..attack.damage_type import DamageType
from ..attack.entity_state import EntityState


class EffectDamage(Effect):

    def __init__(self):
        super().__init__()
        self.returnDamage = 0
        self.lifeSteal = 0

    def apply(self, state):
        # Base damages
        d = (self.value1 + self.jet * self.value2) * (1 + max(0, self.caster.getStrength()) / 100.0) * self.aoe * self.criticalPower * self.targetCount * (1 + self.caster.getPower() / 100.0)

        # Return damage
        if self.target is not self.caster:
            self.returnDamage = java_round(d * self.target.getDamageReturn() / 100.0)

        # Shields
        d -= d * (self.target.getRelativeShield() / 100.0) + self.target.getAbsoluteShield()
        d = max(0, d)

        if self.target.hasState(EntityState.INVINCIBLE):
            d = 0

        self.value = java_round(d)

        if self.target.getLife() < self.value:
            self.value = self.target.getLife()

        # Life steal
        if self.target is not self.caster:
            self.lifeSteal = java_round(self.value * self.caster.getWisdom() / 1000.0)

        erosion = java_round(self.value * self.erosionRate)

        state.log(ActionDamage(DamageType.DIRECT, self.target, self.value, erosion))
        self.target.removeLife(self.value, erosion, self.caster, DamageType.DIRECT, self, self.getItem())
        self.target.onDirectDamage(self.value)
        self.target.onNovaDamage(erosion)

        # Life steal
        if not self.caster.isDead() and self.lifeSteal > 0 and self.caster.getLife() < self.caster.getTotalLife() and not self.caster.hasState(EntityState.UNHEALABLE):

            if self.caster.getLife() + self.lifeSteal > self.caster.getTotalLife():
                self.lifeSteal = self.caster.getTotalLife() - self.caster.getLife()
            if self.lifeSteal > 0:
                state.log(ActionHeal(self.caster, self.lifeSteal))
                self.caster.addLife(self.caster, self.lifeSteal)

        # Return damage
        if self.returnDamage > 0 and not self.caster.hasState(EntityState.INVINCIBLE):

            if self.caster.getLife() < self.returnDamage:
                self.returnDamage = self.caster.getLife()

            returnErosion = java_round(self.returnDamage * self.erosionRate)

            if self.returnDamage > 0:
                state.log(ActionDamage(DamageType.RETURN, self.caster, self.returnDamage, returnErosion))
                self.caster.removeLife(self.returnDamage, returnErosion, self.target, DamageType.RETURN, self, self.getItem())
                self.caster.onNovaDamage(returnErosion)
