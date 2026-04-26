from .action import Action


class ActionEntityDie(Action):

    def __init__(self, leek, killer):
        self.id = leek.getFId()
        self.killer = killer.getFId() if killer is not None else -1

    def getJSON(self):
        retour = []
        retour.append(Action.PLAYER_DEAD)
        retour.append(self.id)
        if self.killer != -1:
            retour.append(self.killer)
        return retour
