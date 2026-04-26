from .action import Action


class ActionMove(Action):

    def __init__(self, leek, path):
        self.leek = leek.getFId()
        self.path = [0] * len(path)
        for i in range(len(path)):
            self.path[i] = path[i].getId()
        self.end = path[len(path) - 1].getId()

    def getJSON(self):
        retour = []
        retour.append(Action.MOVE_TO)
        retour.append(self.leek)
        retour.append(self.end)
        pathArray = []
        for cell in self.path:
            pathArray.append(cell)
        retour.append(pathArray)
        return retour
