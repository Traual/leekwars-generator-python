from .action import Action


class ActionNewTurn(Action):

    def __init__(self, count):
        self.count = count

    def getJSON(self):
        retour = []
        retour.append(Action.NEW_TURN)
        retour.append(self.count)
        return retour
