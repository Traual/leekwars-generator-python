from ..util.util import get_hexa_color


class FarmerLog:

    MAX_LENGTH = 500000
    MAX_SYSTEM_LOGS_AFTER_LIMIT = 10

    MARK = 4
    PAUSE = 5
    MARK_TEXT = 9
    CLEAR_CELLS = 10
    TOO_MUCH_DEBUG = 11

    NO_WEAPON_EQUIPPED = 1000
    CHIP_NOT_EQUIPPED = 1001
    CHIP_NOT_EXISTS = 1002
    WEAPON_NOT_EXISTS = 1003
    WEAPON_NOT_EQUIPPED = 1004
    BULB_WITHOUT_AI = 1005

    def __init__(self, fight, farmer):
        self.mObject = {}
        self.mLogs = None
        self.mAction = -1
        self.mNb = 0
        self.mCurArray = None
        self.mSize = 0
        self.systemLogsAfterLimit = 0
        self.fight = fight
        self.farmer = farmer
        self.tooMuchDebug = False

    def setLogs(self, logs) -> None:
        self.mLogs = logs

    def addAction(self, action) -> None:
        id_ = 0 if self.mLogs is None else max(0, self.mLogs.getNextId() - 1)
        if self.mAction < id_:
            self.mCurArray = []
            self.mObject[str(id_)] = self.mCurArray
            self.mAction = id_
        self.mNb += 1
        self.mCurArray.append(action)

    def _tryBypassLimitForSystemLog(self) -> bool:
        if self.systemLogsAfterLimit >= FarmerLog.MAX_SYSTEM_LOGS_AFTER_LIMIT:
            return False
        self.systemLogsAfterLimit += 1
        return True

    def addSystemLog(self, ai, leek, type_, error, key, parameters):
        # Adapted version: ai may be None in Python
        afterLimit = False
        if not self.addSize(20):
            if not self._tryBypassLimitForSystemLog():
                return
            afterLimit = True

        parametersString = None
        if parameters is not None:
            parametersString = [None] * len(parameters)
            for p in range(len(parameters)):
                parameterString = str(parameters[p]) if parameters[p] is not None else "null"
                if afterLimit or self.addSize(len(parameterString)):
                    parametersString[p] = parameterString
                else:
                    parametersString[p] = "[...]"
        obj = []
        obj.append(leek.getFId())
        obj.append(type_)
        obj.append(error)
        obj.append(key)
        if parameters is not None:
            paramsArray = []
            for param in parametersString:
                paramsArray.append(param)
            obj.append(paramsArray)
        self.addAction(obj)

    def addSystemLogString(self, leek, type_, error, key, parameters) -> None:
        paramSize = 0
        if parameters is not None:
            for p in parameters:
                if p is not None:
                    paramSize += len(p)
        if not self.addSize(20 + paramSize):
            if not self._tryBypassLimitForSystemLog():
                return
        obj = []
        obj.append(leek.getFId())
        obj.append(type_)
        obj.append(error)
        obj.append(key)
        if parameters is not None:
            paramsArray = []
            for param in parameters:
                paramsArray.append(param)
            obj.append(paramsArray)
        self.addAction(obj)

    def addCell(self, leek, cells, color, duration) -> None:
        if not self.addSize(len(cells) * 5 + 8):
            return
        obj = []
        obj.append(leek.getFId())
        obj.append(FarmerLog.MARK)
        cellsArray = []
        for cell in cells:
            cellsArray.append(cell)
        obj.append(cellsArray)
        obj.append(get_hexa_color(color))
        obj.append(duration)
        self.addAction(obj)

    def addClearCells(self, leek) -> None:
        if not self.addSize(8):
            return
        obj = []
        obj.append(leek.getFId())
        obj.append(FarmerLog.CLEAR_CELLS)
        self.addAction(obj)

    def addCellText(self, leek, cells, text, color, duration) -> None:
        if not self.addSize(len(cells) * 5 + 8 + len(text)):
            return
        obj = []
        obj.append(leek.getFId())
        obj.append(FarmerLog.MARK_TEXT)
        cellsArray = []
        for cell in cells:
            cellsArray.append(cell)
        obj.append(cellsArray)
        obj.append(text)
        obj.append(get_hexa_color(color))
        obj.append(duration)
        self.addAction(obj)

    def addLog(self, leek, type_, message, color: int = -1) -> None:
        if message is None:
            return

        if not self.tooMuchDebug and self.mSize != FarmerLog.MAX_LENGTH and self.mSize + 20 + len(message) > FarmerLog.MAX_LENGTH:
            message = message[:max(0, FarmerLog.MAX_LENGTH - (self.mSize + 20 + 6))] + " [...]"
        if not self.addSize(20 + len(message)):
            return

        # In Python version, no AI position info
        obj = []
        obj.append(leek.getFId())
        obj.append(type_)
        obj.append(message)
        if color >= 0:
            obj.append(color)
        self.addAction(obj)

    def addSize(self, size: int) -> bool:
        if self.mSize + size > FarmerLog.MAX_LENGTH:
            if not self.tooMuchDebug:
                self.fight.getState().statistics.tooMuchDebug(self.farmer)
                obj = []
                obj.append(0)
                obj.append(FarmerLog.TOO_MUCH_DEBUG)
                self.addAction(obj)
                self.tooMuchDebug = True
                self.mSize = FarmerLog.MAX_LENGTH
            return False
        self.mSize += size
        return True

    def size(self) -> int:
        return self.mNb

    def toJSON(self):
        return self.mObject

    def addPause(self, leek) -> None:
        if not self.addSize(10):
            return
        obj = []
        obj.append(leek.getFId())
        obj.append(FarmerLog.PAUSE)
        self.addAction(obj)

    def isFull(self) -> bool:
        return self.mSize >= FarmerLog.MAX_LENGTH
