from .entity_ai import EntityAI


class BulbAI(EntityAI):

    def __init__(self, entity, owner_ai, ai_function=None):
        super().__init__(entity, owner_ai.getLogs(), ai_function)
        self.valid = True
        self.mAIFunction = ai_function
        self.setFight(owner_ai.fight)
        self.mOwnerAI = owner_ai

    def runIA(self, session=None):
        if self.mAIFunction is not None:
            self.mOwnerAI.mEntity = self.mEntity
            return self.mAIFunction(self.mOwnerAI)
        return None
