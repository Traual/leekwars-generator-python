from .action import Action


class ActionUseChip(Action):

    def __init__(self, cell, chip, success):
        self.cell = cell.getId()
        self.chip = chip.getTemplate()
        self.success = success

    def getJSON(self):
        retour = []
        retour.append(Action.USE_CHIP)
        retour.append(self.chip)
        retour.append(self.cell)
        retour.append(self.success)
        return retour
