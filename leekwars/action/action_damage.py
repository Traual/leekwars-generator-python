from .action import Action


class ActionDamage(Action):

    def __init__(self, type_, target, pv, erosion):
        self.type = type_
        self.target = target.getFId()
        self.pv = pv
        self.erosion = erosion

    def getJSON(self):
        retour = []
        retour.append(self.type.value)
        retour.append(self.target)
        retour.append(self.pv)
        retour.append(self.erosion)
        return retour
