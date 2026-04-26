import math

from ..state.entity import Entity


class Bulb(Entity):

    TAG = "Bulb"

    def __init__(self, owner, id_, name, level, life, strength, wisdom, agility, resistance, science, magic, cores, ram, tp, mp, skin, hat):
        # Java passes 0 frequency, false metal, 0 face, then team_id, team_name, ai_id, ai_name from owner
        super().__init__(id_, name, owner.getFarmer(), level, life, tp, mp, strength, agility, 0,
                         wisdom, resistance, science, magic, cores, ram, skin, False, 0,
                         owner.getTeamId(), owner.getTeamName(), owner.getAIId(), owner.getAIName(),
                         owner.getFarmerName(), owner.getFarmerCountry(), hat)

        self.setCompositionName(owner.getCompositionName())
        self.mOwner = owner
        self.state = owner.state

    def isSummon(self) -> bool:
        return True

    def getSummoner(self):
        return self.mOwner

    def getType(self) -> int:
        return Entity.TYPE_BULB

    @staticmethod
    def base(base_, bonus, coeff: float) -> int:
        return int(base_ + math.floor(bonus * coeff))

    @staticmethod
    def create(owner, id_, type_, level, critical, name=None):
        from ..bulbs import bulbs as Bulbs
        bulb_template = Bulbs.getInvocationTemplate(type_)
        if bulb_template is not None:
            bulb = bulb_template.createInvocation(owner, id_, level, critical)
            if bulb is not None and name is not None and len(name) > 0:
                bulb.setName(name[:20] if len(name) > 20 else name)
            return bulb
        return None
