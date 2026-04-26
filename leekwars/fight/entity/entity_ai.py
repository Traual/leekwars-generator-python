"""Simplified Python EntityAI.

Replaces the LeekScript-based AI system. A Python AI is any callable
that takes an EntityAI instance and drives the entity's turn through
the EntityAI methods (which expose the same API as LeekScript classes
like FightClass, NetworkClass, FieldClass, EntityClass...).

Usage:
    def my_ai(ai):
        # ai is an EntityAI instance
        # ai.entity() / ai.fight / ai.getState() are accessible
        # The AI calls fight functions via the bound API
        ...

    ai = EntityAI(entity, logs, ai_function=my_ai)
"""

import time

from ..fight import Fight  # forward; resolved via TYPE_CHECKING in real use
from ...action.action_ai_error import ActionAIError


class LeekMessage:

    def __init__(self, author, type_, message):
        self.mAuthor = author
        self.mType = type_
        self.mMessage = message

    def getAuthor(self):
        return self.mAuthor

    def getType(self):
        return self.mType

    def getMessage(self):
        return self.mMessage


class EntityAI:

    TAG = "EntityAI"

    def __init__(self, entity=None, logs=None, ai_function=None):
        self.mInitialEntity = entity
        self.mEntity = entity
        self.fight = entity.getFight() if entity is not None else None
        self.ai_function = ai_function
        self.logs = logs

        self.mIARunTime = 0
        self.mIACpuRunTime = 0

        self.ai_name = ""
        self.mMessages = []
        self.mSays = []
        self.valid = ai_function is not None
        self.isFirstRuntimeError = True
        self.staticInitialized = False

        # Operations counters for parity with Java AI
        self.operations = 0
        self.maxOperations = 0
        self.maxRAM = 0

        # Mimic Java getId() on AI
        self.id = entity.getFId() if entity is not None else 0

        # Compile/analyze times (for outcome reporting)
        self._analyzeTime = 0
        self._compileTime = 0

    @staticmethod
    def resolve(generator, entityInfo, entity):
        """In Python version, the AI function is provided directly via entityInfo.ai_function.
        Returns the function (or None) to be used as the AI."""
        return getattr(entityInfo, 'ai_function', None)

    @staticmethod
    def build(generator, ai_function, entity):
        """Build an EntityAI for the given entity with a Python AI function."""
        ai = EntityAI(entity, entity.getLogs(), ai_function)
        ai.valid = ai_function is not None
        return ai

    def leek(self):
        return self.mEntity

    def getUAI(self):
        return self

    def setLogs(self, leekLog) -> None:
        self.logs = leekLog

    def setEntity(self, entity) -> None:
        self.mEntity = entity
        self.mInitialEntity = entity
        self.fight = entity.getFight()

    def addSystemLog(self, type_, error, parameters=None) -> None:
        # Simplified: directly forward to logs
        if parameters is None:
            parameters = []
        if self.logs is not None:
            error_value = error.value if hasattr(error, 'value') else int(error) if isinstance(error, int) else 0
            self.logs.addSystemLog(type_, "", error_value, parameters)

    def getIARunTime(self) -> int:
        return self.mIARunTime

    def getIACpuRunTime(self) -> int:
        return self.mIACpuRunTime // 1000000

    def isValid(self) -> bool:
        return self.valid

    def getLogs(self):
        return self.logs

    def addMessage(self, leekMessage) -> None:
        if len(self.mMessages) > 200:
            return
        self.mMessages.append(leekMessage)

    def getSays(self):
        return self.mSays

    def setFight(self, fight) -> None:
        self.fight = fight
        if self.logs is not None:
            self.logs.setLogs(fight.getState().getActions())

    def runTurn(self, turn: int) -> None:
        startTime = time.perf_counter_ns()
        try:
            self.mEntity = self.mInitialEntity
            if not self.staticInitialized:
                self.staticInit()
                self.staticInitialized = True
            self.runIA(None)
        except Exception as e:
            self.fight.log(ActionAIError(self.mEntity))
            self.fight.getState().statistics.error(self.mEntity)
            try:
                self.fight.generator.exception(e, self.fight, self.mEntity.getFarmer(), None)
            except Exception:
                pass

        self.mSays.clear()
        self.mMessages.clear()

        endTime = time.perf_counter_ns()
        self.mIARunTime += (endTime - startTime)

    def staticInit(self) -> None:
        # Override in subclasses if needed
        pass

    def getEntity(self):
        return self.mEntity

    def getFight(self):
        return self.fight

    def isTest(self) -> bool:
        return self.mEntity.getId() < 0

    def runIA(self, session=None):
        if self.ai_function is not None:
            return self.ai_function(self)
        return None

    def getMessages(self):
        return self.mMessages

    def getState(self):
        return self.fight.getState()

    def getDate(self):
        return self.getState().getDate()

    def getAnalyzeTime(self) -> int:
        return self._analyzeTime

    def getCompileTime(self) -> int:
        return self._compileTime
