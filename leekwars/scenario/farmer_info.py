class FarmerInfo:

    def __init__(self):
        self.id = 0
        self.name = ""
        self.country = ""

    def toJson(self):
        json = {}
        json["id"] = self.id
        json["name"] = self.name
        json["country"] = self.country
        return json
