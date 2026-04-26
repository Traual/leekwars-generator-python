from .action import Action


class ActionRemovePoisons(Action):

    def __init__(self, target):
        self.id = target.getFId()

    def getJSON(self):
        retour = []
        retour.append(Action.REMOVE_POISONS)
        retour.append(self.id)
        return retour
