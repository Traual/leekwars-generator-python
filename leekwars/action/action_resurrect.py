from .action import Action


class ActionResurrect(Action):

    def __init__(self, owner, target):
        self.owner = owner.getFId()
        self.target = target.getFId()
        self.cell = target.getCell().getId()
        self.life = target.getLife()
        self.max_life = target.getTotalLife()

    def getJSON(self):
        retour = []
        retour.append(Action.RESURRECT)
        retour.append(self.owner)
        retour.append(self.target)
        retour.append(self.cell)
        retour.append(self.life)
        retour.append(self.max_life)
        return retour
