from .action import Action


class ActionInvocation(Action):

    def __init__(self, target, result):
        self.owner = target.getSummoner().getFId()
        self.target = target.getFId()
        self.cell = target.getCell().getId()
        self.result = result

    def getJSON(self):
        retour = []
        retour.append(Action.SUMMON)
        retour.append(self.owner)
        retour.append(self.target)
        retour.append(self.cell)
        retour.append(self.result)
        return retour
