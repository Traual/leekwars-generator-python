from .action import Action
from ..util.util import get_hexa_color


class ActionShowCell(Action):

    def __init__(self, cell, color):
        self.mCell = cell
        self.mColor = color

    def getJSON(self):
        retour = []
        retour.append(Action.SHOW_CELL)
        retour.append(self.mCell)
        retour.append(get_hexa_color(self.mColor))
        return retour
