import random as py_random
import time

from .farmer_info import FarmerInfo
from .team_info import TeamInfo
from .entity_info import EntityInfo
from ..util import json_util as Json
from ..util import util as Util


class Scenario:

    TAG = "Scenario"

    _leekwars_farmer = FarmerInfo()
    _leekwars_farmer.id = 0
    _leekwars_farmer.name = "Leek Wars"
    _leekwars_farmer.country = "fr"

    def __init__(self):
        # Between 1 and MAX_VALUE (included)
        self.seed = 1 + int((py_random.random() * time.time_ns()) % (2 ** 31 - 1))
        self.maxTurns = 64
        self.type = 0
        self.context = 0
        self.fightID = 0
        self.boss = 0
        self.farmers = {}
        self.teams = {}
        self.entities = []
        self.map = None
        self.drawCheckLife = False

    @staticmethod
    def fromFile(file):
        scenario = Scenario()

        json = Json.parse_object(Util.read_file(file))

        if "random_seed" in json:
            scenario.seed = json["random_seed"]
        if "max_turns" in json:
            scenario.maxTurns = json["max_turns"]
        for farmerJson in json["farmers"]:
            farmer = FarmerInfo()
            farmer.id = farmerJson["id"]
            farmer.name = farmerJson["name"]
            farmer.country = farmerJson["country"]
            scenario.farmers[farmer.id] = farmer
        for teamJson in json["teams"]:
            team = TeamInfo()
            team.id = teamJson["id"]
            team.name = teamJson["name"]
            if "composition_name" in teamJson and teamJson["composition_name"] is not None:
                team.compositionName = teamJson["composition_name"]
            scenario.teams[team.id] = team
        for teamJson in json["entities"]:
            team = []
            for entityJson in teamJson:
                entity = EntityInfo(entityJson)
                team.append(entity)
            scenario.entities.append(team)
        return scenario

    def addEntity(self, teamID: int, entity) -> None:
        if entity is None or teamID < 0:
            return
        while len(self.entities) < teamID + 1:
            self.entities.append([])
        self.entities[teamID].append(entity)

    def setEntityAI(self, team: int, leek_id: int, aiName, aiFolder, aiPath, aiOwner, aiVersion, aiStrict) -> None:
        for entity in self.entities[team]:
            if entity.id == leek_id:
                entity.ai = aiName
                entity.ai_folder = aiFolder
                entity.ai_path = aiPath
                entity.aiOwner = aiOwner
                entity.ai_version = aiVersion
                entity.ai_strict = aiStrict

    def toJson(self):
        json = {}
        farmers = []
        for farmer in self.farmers.values():
            farmers.append(farmer.toJson())
        json["farmers"] = farmers
        teams = []
        for team in self.teams.values():
            teams.append(team.toJson())
        json["teams"] = teams
        entities = []
        for list_ in self.entities:
            team = []
            for entity in list_:
                team.append(entity.toJson())
            entities.append(team)
        json["entities"] = entities
        return json

    def __str__(self) -> str:
        return Json.to_json(self.toJson())

    def getFarmer(self, farmer: int):
        if farmer == 0:
            return Scenario._leekwars_farmer
        return self.farmers.get(farmer)

    def setDrawCheckLife(self, drawCheckLife: bool) -> None:
        self.drawCheckLife = drawCheckLife
