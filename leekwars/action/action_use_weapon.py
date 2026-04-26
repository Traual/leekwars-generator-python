from .action import Action


class ActionUseWeapon(Action):

    def __init__(self, cell, success):
        self.cell = cell.getId()
        self.success = success

    def getJSON(self):
        retour = []
        retour.append(Action.USE_WEAPON)
        retour.append(self.cell)
        retour.append(self.success)
        return retour
