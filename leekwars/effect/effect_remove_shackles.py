from .effect import Effect
from ..action.action_remove_shackles import ActionRemoveShackles


class EffectRemoveShackles(Effect):

    def apply(self, state):
        self.target.removeShackles()
        # "Les entraves de X sont retirées"
        state.log(ActionRemoveShackles(self.target))
