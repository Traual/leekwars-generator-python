from .effect import Effect


class EffectPermutation(Effect):

    def apply(self, fight):
        fight.invertEntities(self.caster, self.target)
