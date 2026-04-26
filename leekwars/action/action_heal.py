from .action import Action


class ActionHeal(Action):

    def __init__(self, target, life):
        self.target = target.getFId()
        self.life = life

    def getJSON(self):
        retour = []
        retour.append(Action.HEAL)
        retour.append(self.target)
        retour.append(self.life)
        return retour
