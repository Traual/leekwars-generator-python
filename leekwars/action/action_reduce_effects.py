from .action import Action


class ActionReduceEffects(Action):

    def __init__(self, target, value):
        self.id = target.getFId()
        self.value = value

    def getJSON(self):
        retour = []
        retour.append(Action.REDUCE_EFFECTS)
        retour.append(self.id)
        retour.append(self.value)
        return retour
