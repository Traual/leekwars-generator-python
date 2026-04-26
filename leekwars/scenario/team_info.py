class TeamInfo:

    def __init__(self):
        self.id = 0
        self.name = ""
        self.compositionName = None
        self.level = 0
        self.turretAIPath = None
        self.turretAIOwner = 0

    def toJson(self):
        json = {}
        json["id"] = self.id
        json["name"] = self.name
        if self.compositionName is not None:
            json["composition_name"] = self.compositionName
        json["level"] = self.level
        return json
