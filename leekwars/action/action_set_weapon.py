from .action import Action


class ActionSetWeapon(Action):

    def __init__(self, weapon):
        self.leek = 0
        self.weapon = weapon.getTemplate()

    def getJSON(self):
        retour = []
        retour.append(Action.SET_WEAPON)
        retour.append(self.weapon)
        return retour
