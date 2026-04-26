from ..util import json_util as Json


class Outcome:
    """Fight outcome with public data, logs, statistics."""

    def __init__(self):
        # Fight: public data: entities, map, actions, flags, duration, ai times
        self.fight = None
        # Logs: debugs, marks, pauses
        self.logs = {}
        # Winner team id
        self.winner = -1
        # Duration
        self.duration = 0
        # Fight statistics
        self.statistics = None
        # Exception
        self.exception = None

        self.analyzeTime = 0
        self.compilationTime = 0
        self.executionTime = 0

    def toJson(self):
        json = {}
        logsJSON = {}
        for k, v in self.logs.items():
            logsJSON[str(k)] = v.toJSON()
        json["fight"] = self.fight.toJSON() if self.fight is not None else None
        json["logs"] = logsJSON
        json["winner"] = self.winner
        json["duration"] = self.duration
        json["analyze_time"] = self.analyzeTime
        json["compilation_time"] = self.compilationTime
        json["execution_time"] = self.executionTime
        return json

    def __str__(self) -> str:
        return Json.to_json(self.toJson())
