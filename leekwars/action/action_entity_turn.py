from .action import Action


class ActionEntityTurn(Action):

    def __init__(self, leek):
        if leek is None:
            self.id = -1
        else:
            self.id = leek.getFId()

    def getJSON(self):
        retour = []
        retour.append(Action.LEEK_TURN)
        retour.append(self.id)
        return retour
