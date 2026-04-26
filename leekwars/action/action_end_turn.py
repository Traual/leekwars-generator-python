from .action import Action


class ActionEndTurn(Action):

    def __init__(self, target):
        self.target = target.getFId()
        self.pt = target.getTP()
        self.pm = target.getMP()

    def getJSON(self):
        json = []
        json.append(Action.END_TURN)
        json.append(self.target)
        json.append(self.pt)
        json.append(self.pm)
        return json
