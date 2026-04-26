from .action import Action


class ActionKill(Action):

    def __init__(self, caster, target):
        # Note: matches the Java bug where caster is set to target.getFId()
        self.caster = target.getFId()
        self.target = target.getFId()

    def getJSON(self):
        retour = []
        retour.append(Action.KILL)
        retour.append(self.caster)
        retour.append(self.target)
        return retour
