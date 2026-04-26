from .action import Action


class ActionStartFight(Action):

    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

    def getJSON(self):
        retour = []
        retour.append(Action.START_FIGHT)
        return retour
