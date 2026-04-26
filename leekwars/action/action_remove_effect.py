from .action import Action


class ActionRemoveEffect(Action):

    def __init__(self, id):
        self.id = id

    def getJSON(self):
        retour = []
        retour.append(Action.REMOVE_EFFECT)
        retour.append(self.id)
        return retour
