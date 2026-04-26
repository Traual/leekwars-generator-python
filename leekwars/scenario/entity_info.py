from ..leek.leek import Leek
from ..entity.bulb import Bulb
from ..turret.turret import Turret
from ..weapons import weapons as Weapons
from ..chips import chips as Chips


class EntityInfo:

    TAG = "EntityInfo"

    classes = [Leek, Bulb, Turret]

    def __init__(self, e=None):
        self.id = 0
        self.name = ""
        self.ai = None
        self.ai_function = None  # Python AI - replacement for LeekScript
        self.ai_folder = 0
        self.ai_path = None
        self.ai_version = 0
        self.ai_strict = False
        self.aiOwner = 0
        self.type = 0
        self.farmer = 0
        self.team = 0
        self.level = 0
        self.dead = False
        self.life = 0
        self.tp = 0
        self.mp = 0
        self.strength = 0
        self.agility = 0
        self.frequency = 0
        self.wisdom = 0
        self.resistance = 0
        self.science = 0
        self.magic = 0
        self.cores = 0
        self.ram = 0
        self.chips = []
        self.weapons = []
        self.cell = None
        self.skin = 0
        self.hat = 0
        self.metal = False
        self.face = 0
        self.customClass = None
        self.orientation = 0

        if e is not None:
            self._init_from_json(e)

    def _init_from_json(self, e):
        if "id" in e:
            self.id = e["id"]
        self.name = e["name"]
        if "ai" in e:
            self.ai = e["ai"]
        if "ai_folder" in e:
            self.ai_folder = e["ai_folder"]
        if "ai_path" in e and e["ai_path"] is not None:
            self.ai_path = e["ai_path"]
        if "ai_version" in e and e["ai_version"] is not None:
            self.ai_version = e["ai_version"]
        if "ai_strict" in e and e["ai_strict"] is not None:
            self.ai_strict = e["ai_strict"]
        if "farmer" in e and e["farmer"] is not None:
            self.farmer = e["farmer"]
        if "team" in e and e["team"] is not None:
            self.team = e["team"]
        self.level = e["level"]
        self.life = e["life"]
        self.tp = e["tp"]
        self.mp = e["mp"]
        self.strength = e["strength"]
        if "agility" in e:
            self.agility = e["agility"]
        if "frequency" in e:
            self.frequency = e["frequency"]
        if "wisdom" in e:
            self.wisdom = e["wisdom"]
        if "resistance" in e:
            self.resistance = e["resistance"]
        if "science" in e:
            self.science = e["science"]
        if "magic" in e:
            self.magic = e["magic"]
        if "cores" in e:
            self.cores = e["cores"]
        if "ram" in e:
            self.ram = e["ram"]

        weapons = e.get("weapons")
        if weapons is not None:
            for w in weapons:
                self.weapons.append(w)
        chips = e.get("chips")
        if chips is not None:
            for c in chips:
                self.chips.append(c)
        if "cell" in e and e["cell"] is not None:
            self.cell = e["cell"]

    def createEntity(self, generator, scenario, fight):
        try:
            clazz = self.customClass if self.customClass is not None else EntityInfo.classes[self.type]
            entity = clazz()
        except Exception as e:
            generator.exception(e, fight)
            return None
        entity.setId(self.id)
        entity.setName(self.name)
        entity.setLevel(self.level)
        entity.setTotalLife(self.life)
        entity.setLife(self.life)
        entity.setStrength(self.strength)
        entity.setAgility(self.agility)
        entity.setWisdom(self.wisdom)
        entity.setResistance(self.resistance)
        entity.setScience(self.science)
        entity.setMagic(self.magic)
        entity.setFrequency(self.frequency)
        entity.setCores(self.cores)
        entity.setRAM(self.ram)
        entity.setTP(self.tp)
        entity.setMP(self.mp)
        entity.setFarmer(self.farmer)
        entity.setDead(self.dead)
        entity.setOrientation(self.orientation)
        if self.farmer >= 0:
            farmer = scenario.getFarmer(self.farmer)
            if farmer is not None:
                entity.setFarmerName(farmer.name)
                entity.setFarmerCountry(farmer.country)
        entity.setAIName(self.ai if self.ai is not None else "")
        entity.setTeamID(self.team)
        if self.team > 0 and self.team in scenario.teams:
            entity.setTeamName(scenario.teams[self.team].name)
            entity.setCompositionName(scenario.teams[self.team].compositionName)
        entity.setSkin(self.skin)
        entity.setHat(self.hat)
        entity.setMetal(self.metal)
        entity.setFace(self.face)
        entity.setInitialCell(self.cell)

        for w in self.weapons:
            weapon = Weapons.getWeapon(w)
            if weapon is None:
                pass
            else:
                entity.addWeapon(weapon)
        for c in self.chips:
            entity.addChip(Chips.getChip(c))

        return entity

    def toJson(self):
        json = {}
        json["id"] = self.id
        json["name"] = self.name
        json["level"] = self.level
        json["strength"] = self.strength
        json["agility"] = self.agility
        json["wisdom"] = self.wisdom
        json["resistance"] = self.resistance
        json["science"] = self.science
        json["magic"] = self.magic
        json["frequency"] = self.frequency
        json["cores"] = self.cores
        json["ram"] = self.ram
        json["tp"] = self.tp
        json["mp"] = self.mp
        json["farmer"] = self.farmer
        json["team"] = self.team
        json["ai"] = self.ai
        json["ai_folder"] = self.ai_folder
        json["ai_owner"] = self.aiOwner
        json["ai_version"] = self.ai_version
        json["ai_strict"] = self.ai_strict
        json["weapons"] = list(self.weapons)
        json["chips"] = list(self.chips)
        return json
