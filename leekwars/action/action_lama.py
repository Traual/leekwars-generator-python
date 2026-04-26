from .action import Action


class ActionLama(Action):

    def __init__(self):
        pass

    def getJSON(self):
        retour = []
        retour.append(Action.LAMA)
        return retour
