# Simplified LeekLog: no LeekScript runtime dependency.
# In our Python version, AIs are pure Python code, so the AILog
# layer is reduced to delegating to FarmerLog.


class LeekLog:

    STANDARD = 0

    def __init__(self, farmer_logs, entity):
        self.farmerLogs = farmer_logs
        self.entity = entity

    def addLog(self, *args):
        # Two overloads:
        # (warning, string)  -> simple log
        # (type, message, color) -> log with color
        if len(args) == 2:
            warning, string = args
            self.farmerLogs.addLog(self.entity, warning, string)
        elif len(args) == 3:
            type_, message, color = args
            self.farmerLogs.addLog(self.entity, LeekLog.STANDARD, message, color)

    def addSystemLog(self, *args):
        # Match Java overloads
        if len(args) == 2:
            type_, error = args
            self.addSystemLog(type_, "", error.value if hasattr(error, 'value') else int(error), None)
        elif len(args) == 3:
            type_, error, parameters = args
            self.addSystemLog(type_, "", error.value if hasattr(error, 'value') else int(error), parameters)
        elif len(args) == 4:
            type_, trace, key, parameters = args
            self.farmerLogs.addSystemLogString(self.entity, type_, trace, key, parameters)

    def setLogs(self, actions) -> None:
        self.farmerLogs.setLogs(actions)

    def addCell(self, cells, color, duration) -> None:
        self.farmerLogs.addCell(self.entity, cells, color, duration)

    def addClearCells(self) -> None:
        self.farmerLogs.addClearCells(self.entity)

    def addCellText(self, cells, text, color, duration) -> None:
        self.farmerLogs.addCellText(self.entity, cells, text, color, duration)

    def addPause(self) -> None:
        self.farmerLogs.addPause(self.entity)

    def isFull(self) -> bool:
        return self.farmerLogs.isFull()

    def setStream(self, stream) -> None:
        pass
