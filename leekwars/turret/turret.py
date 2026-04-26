from ..state.entity import Entity


class Turret(Entity):

    def __init__(self):
        super().__init__()

    def startFight(self) -> None:
        from ..effect.effect import Effect
        from ..attack.entity_state import EntityState

        Effect.createEffect(self.state, Effect.TYPE_ADD_STATE, -1, 1, EntityState.STATIC.value, 0, False,
                            self, self, None, 0, False, 0, 1, 0, Effect.MODIFIER_IRREDUCTIBLE)

    def getType(self) -> int:
        return Entity.TYPE_TURRET
