import math

from ..chips import chips as Chips


class BulbTemplate:

    def __init__(self, id_, name, chips, characteristics):
        self.mId = id_
        self.mName = name

        self.mMinLife = characteristics["life"][0]
        self.mMaxLife = characteristics["life"][1]

        self.mMinStrength = characteristics["strength"][0]
        self.mMaxStrength = characteristics["strength"][1]

        self.mMinWisdom = characteristics["wisdom"][0]
        self.mMaxWisdom = characteristics["wisdom"][1]

        self.mMinAgility = characteristics["agility"][0]
        self.mMaxAgility = characteristics["agility"][1]

        self.mMinResistance = characteristics["resistance"][0]
        self.mMaxResistance = characteristics["resistance"][1]

        self.mMinScience = characteristics["science"][0]
        self.mMaxScience = characteristics["science"][1]

        self.mMinMagic = characteristics["magic"][0]
        self.mMaxMagic = characteristics["magic"][1]

        self.mMinTp = characteristics["tp"][0]
        self.mMaxTp = characteristics["tp"][1]

        self.mMinMp = characteristics["mp"][0]
        self.mMaxMp = characteristics["mp"][1]

        self.mChips = []
        if chips is not None:
            for i in chips:
                if i is not None:
                    template = Chips.getChip(int(i))
                    self.mChips.append(template)

    def getId(self) -> int:
        return self.mId

    def getName(self) -> str:
        return self.mName

    @staticmethod
    def base(base, bonus, coeff: float, multiplier: float) -> int:
        return int((base + math.floor((bonus - base) * coeff)) * multiplier)

    def createInvocation(self, owner, id_, level, critical: bool):
        from ..entity.bulb import Bulb
        c = min(300.0, owner.getLevel()) / 300.0
        multiplier = 1.2 if critical else 1.0

        inv = Bulb(owner, id_, self.mName, level,
                   BulbTemplate.base(self.mMinLife, self.mMaxLife, c, multiplier),
                   BulbTemplate.base(self.mMinStrength, self.mMaxStrength, c, multiplier),
                   BulbTemplate.base(self.mMinWisdom, self.mMaxWisdom, c, multiplier),
                   BulbTemplate.base(self.mMinAgility, self.mMaxAgility, c, multiplier),
                   BulbTemplate.base(self.mMinResistance, self.mMaxResistance, c, multiplier),
                   BulbTemplate.base(self.mMinScience, self.mMaxScience, c, multiplier),
                   BulbTemplate.base(self.mMinMagic, self.mMaxMagic, c, multiplier),
                   1,
                   6,
                   BulbTemplate.base(self.mMinTp, self.mMaxTp, c, multiplier),
                   BulbTemplate.base(self.mMinMp, self.mMaxMp, c, multiplier),
                   self.mId, 0)

        for chip in self.mChips:
            inv.addChip(chip)

        return inv

    def getChips(self):
        return self.mChips

    def getMinLife(self) -> int: return self.mMinLife
    def getMaxLife(self) -> int: return self.mMaxLife
    def getMinStrength(self) -> int: return self.mMinStrength
    def getMaxStrength(self) -> int: return self.mMaxStrength
    def getMinWisdom(self) -> int: return self.mMinWisdom
    def getMaxWisdom(self) -> int: return self.mMaxWisdom
    def getMinAgility(self) -> int: return self.mMinAgility
    def getMaxAgility(self) -> int: return self.mMaxAgility
    def getMinResistance(self) -> int: return self.mMinResistance
    def getMaxResistance(self) -> int: return self.mMaxResistance
    def getMinScience(self) -> int: return self.mMinScience
    def getMaxScience(self) -> int: return self.mMaxScience
    def getMinMagic(self) -> int: return self.mMinMagic
    def getMaxMagic(self) -> int: return self.mMaxMagic
    def getMinTp(self) -> int: return self.mMinTp
    def getMaxTp(self) -> int: return self.mMaxTp
    def getMinMp(self) -> int: return self.mMinMp
    def getMaxMp(self) -> int: return self.mMaxMp
