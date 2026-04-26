from .action import Action


class ActionSay(Action):

    def __init__(self, message):
        self.message = message

    def getJSON(self):
        retour = []
        retour.append(Action.SAY)
        retour.append(self.message.replace("\t", "    "))
        return retour
