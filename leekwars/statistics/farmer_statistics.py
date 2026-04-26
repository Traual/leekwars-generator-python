from ..util import json_util as Json


class FarmerStatistics:
    """Object to keep track of farmer statistics during the fight."""

    def __init__(self):
        self.teleportations = 0
        self.summons = 0
        self.weaponShot = 0
        self.usedChips = 0
        self.suicides = 0
        self.kills = 0
        self.kamikaze = 0
        self.killedAllies = 0
        self.healedEnemies = 0
        self.maxHurtEnemies = 0
        self.maxKilledEnemies = 0
        self.walkedDistance = 0
        self.damage = 0
        self.tooMuchOperations = 0
        self.stackOverflows = 0
        self.weaponsUsed = {}  # leek_id -> set of weapon ids
        self.chipsUsed = {}    # leek_id -> set of chip ids
        self.endCells = {}     # leek_id -> cell_id
        self.endLifes = {}     # leek_id -> life
        self.totalLifes = {}   # leek_id -> total life
        self.walkedCells = {}  # leek_id -> set of cell ids
        self.aiInstructions = {}
        self.aiOperations = {}
        self.aiTimes = {}

    def add_to_set(self, dict_, leek: int, value: int) -> None:
        if leek not in dict_:
            dict_[leek] = set()
        dict_[leek].add(value)

    def increment_value(self, dict_, leek: int, amount: int) -> None:
        dict_[leek] = dict_.get(leek, 0) + amount

    def toJson(self):
        json = {}
        json["teleporatations"] = self.teleportations
        json["summons"] = self.summons
        json["weaponShot"] = self.weaponShot
        json["usedChips"] = self.usedChips
        json["suicides"] = self.suicides
        json["kills"] = self.kills
        json["kamikaze"] = self.kamikaze
        json["killedAllies"] = self.killedAllies
        json["healedEnemies"] = self.healedEnemies
        json["maxHurtEnemies"] = self.maxHurtEnemies
        json["maxKilledEnemies"] = self.maxKilledEnemies
        json["walkedDistance"] = self.walkedDistance
        json["damage"] = self.damage
        json["tooMuchOperations"] = self.tooMuchOperations
        json["stackOverflows"] = self.stackOverflows
        json["weaponsUsed"] = {str(k): list(v) for k, v in self.weaponsUsed.items()}
        json["chipsUsed"] = {str(k): list(v) for k, v in self.chipsUsed.items()}
        json["endCells"] = {str(k): v for k, v in self.endCells.items()}
        json["endLifes"] = {str(k): v for k, v in self.endLifes.items()}
        json["totalLifes"] = {str(k): v for k, v in self.totalLifes.items()}
        json["walkedCells"] = {str(k): sorted(list(v)) for k, v in self.walkedCells.items()}
        json["aiInstructions"] = {str(k): v for k, v in self.aiInstructions.items()}
        json["aiOperations"] = {str(k): v for k, v in self.aiOperations.items()}
        json["aiTimes"] = {str(k): v for k, v in self.aiTimes.items()}
        return json
