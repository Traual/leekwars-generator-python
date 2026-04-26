from .effect import Effect
from ..action.action_remove_poisons import ActionRemovePoisons


class EffectAntidote(Effect):

    def apply(self, state):
        self.target.clearPoisons(self.caster)

        # "Les poisons de X sont neutralisés"
        state.log(ActionRemovePoisons(self.target))
