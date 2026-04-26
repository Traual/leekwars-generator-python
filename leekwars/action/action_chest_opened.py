from .action import Action


class ActionChestOpened(Action):

    def __init__(self, killer, chest, resources):
        self.killer = killer
        self.chest = chest
        self.resources = resources

    def getJSON(self):
        retour = []
        retour.append(Action.CHEST_OPENED)
        retour.append(self.killer.getFId())
        retour.append(self.chest.getFId())
        res = {}
        for k, v in self.resources.items():
            res[str(k)] = v
        retour.append(res)
        return retour
