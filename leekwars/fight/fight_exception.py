class FightException(Exception):

    NOT_ENOUGHT_PLAYERS = 1
    CANT_START_FIGHT = 2

    def __init__(self, type_: int):
        self.type = type_

    def get_message(self) -> str:
        if self.type == FightException.NOT_ENOUGHT_PLAYERS:
            return "Pas assez de joueurs"
        elif self.type == FightException.CANT_START_FIGHT:
            return "Toutes les conditions ne sont pas remplies pour démarrer le combat"
        return ""

    def __str__(self) -> str:
        return self.get_message()

    def getType(self) -> int:
        return self.type
