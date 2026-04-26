from .effect import Effect
from ..attack.entity_state import EntityState


class EffectAddState(Effect):

    def apply(self, state):
        self.value = int(self.value1)
        self.state = EntityState(int(self.value1))
        self.target.addState(self.state)
