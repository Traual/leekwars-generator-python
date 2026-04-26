from .action import Action


class ActionAIError(Action):

    def __init__(self, leek):
        if leek is None:
            self.id = -1
        else:
            self.id = leek.getFId()

    def getJSON(self):
        retour = []
        retour.append(Action.AI_ERROR)
        retour.append(self.id)
        return retour
