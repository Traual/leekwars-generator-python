from ..util import json_util as Json


class Registers:

    MAX_ENTRIES = 100
    MAX_KEY_LENGTH = 100
    MAX_DATA_LENGTH = 5000

    def __init__(self, new_register: bool = False):
        self.mValues = {}
        self.mModified = False
        self.mNew = new_register

    def isNew(self) -> bool:
        return self.mNew

    def isModified(self) -> bool:
        return self.mModified

    def getValues(self):
        return self.mValues

    def set(self, key: str, value: str) -> bool:
        if len(self.mValues) > Registers.MAX_ENTRIES:
            return False
        if len(key) > Registers.MAX_KEY_LENGTH:
            return False
        if len(value) > Registers.MAX_DATA_LENGTH:
            return False
        val = self.mValues.get(key)
        if val is not None:
            if value == val:
                return True
        self.mModified = True
        self.mValues[key] = value
        return True

    def get(self, key: str):
        return self.mValues.get(key)

    def delete(self, key: str) -> bool:
        if key not in self.mValues:
            return False
        del self.mValues[key]
        self.mModified = True
        return True

    def toJSONString(self) -> str:
        # TreeMap is naturally sorted, mimic this with sort_keys
        return Json.to_json(dict(sorted(self.mValues.items())))

    @staticmethod
    def fromJSONString(value: str):
        register = Registers()
        try:
            datas = Json.parse_object(value)
            for key, val in datas.items():
                register.mValues[key] = str(val)
        except Exception:
            pass
        return register
