from .action import Action


class ActionUpdateEffect(Action):

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def getJSON(self):
        retour = []
        retour.append(Action.UPDATE_EFFECT)
        retour.append(self.id)
        retour.append(self.value)
        return retour
