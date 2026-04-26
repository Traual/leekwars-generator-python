from .effect import Effect
from ..action.action_kill import ActionKill
from ..attack.damage_type import DamageType


class EffectKill(Effect):

    def apply(self, state):
        # if not self.target.hasState(EntityState.INVINCIBLE):  # Graal
        self.value = self.target.getLife()
        state.log(ActionKill(self.caster, self.target))
        self.target.removeLife(self.value, 0, self.caster, DamageType.DIRECT, self, self.getItem())
