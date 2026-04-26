from .action import Action


class ActionRemoveShackles(Action):

    def __init__(self, target):
        self.id = target.getFId()

    def getJSON(self):
        retour = []
        retour.append(Action.REMOVE_SHACKLES)
        retour.append(self.id)
        return retour
