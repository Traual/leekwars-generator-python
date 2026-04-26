import time

from ..state.state import State
from ..action.action_ai_error import ActionAIError
from ..action.action_entity_turn import ActionEntityTurn
from ..action.action_end_turn import ActionEndTurn
from ..effect.effect import Effect
from .fight_exception import FightException


class Fight:

    TAG = "Fight"

    # Maximum number of turns
    MAX_TURNS = 64

    # Fight full types (type + context)
    TYPE_SOLO_GARDEN = 1
    TYPE_SOLO_TEST = 2
    TYPE_NORMAL_WHAT = 3
    TYPE_TEAM_GARDEN = 4
    TYPE_SOLO_CHALLENGE = 5
    TYPE_FARMER_GARDEN = 6
    TYPE_SOLO_TOURNAMENT = 7
    TYPE_TEAM_TEST = 8
    TYPE_FARMER_TOURNAMENT = 9
    TYPE_TEAM_TOURNAMENT = 10
    TYPE_FARMER_CHALLENGE = 11
    TYPE_FARMER_TEST = 12
    FULL_TYPE_BATTLE_ROYALE = 15

    # Fight contexts
    CONTEXT_TEST = 0
    CONTEXT_CHALLENGE = 1
    CONTEXT_GARDEN = 2
    CONTEXT_TOURNAMENT = 3
    CONTEXT_BATTLE_ROYALE = 5

    # Fight types
    TYPE_SOLO = 0
    TYPE_FARMER = 1
    TYPE_TEAM = 2
    TYPE_BATTLE_ROYALE = 3
    TYPE_BOSS = 4
    TYPE_WAR = 5
    TYPE_CHEST_HUNT = 6
    TYPE_COLOSSUS = 7

    # Flags
    FLAG_STATIC = 1
    FLAG_PERFECT = 2

    # Summon limit
    SUMMON_LIMIT = 8

    MAX_LOG_COUNT = 5000

    def __init__(self, generator, listener=None):
        self.mWinteam = -1
        self.generator = generator
        self.mId = 0
        self.mBoss = 0
        self.mStartFarmer = -1
        self.max_turns = Fight.MAX_TURNS
        self.executionTime = 0
        self.listener = listener
        self.state = State()

    def addFlag(self, team: int, flag: int) -> None:
        self.state.getTeams()[team].addFlag(flag)

    def getFlags(self, team: int):
        return self.state.getTeams()[team].getFlags()

    def getWinner(self) -> int:
        return self.mWinteam

    def setTeamID(self, team: int, id_: int) -> None:
        if team < len(self.state.getTeams()):
            self.state.getTeams()[team].setID(id_)

    def setStartFarmer(self, startFarmer: int) -> None:
        self.mStartFarmer = startFarmer

    def getStartFarmer(self) -> int:
        return self.mStartFarmer

    def getTeamID(self, team: int) -> int:
        if team < len(self.state.getTeams()):
            return self.state.getTeams()[team].getID()
        return -1

    def getId(self) -> int:
        return self.mId

    def getBoss(self) -> int:
        return self.mBoss

    def log(self, log) -> None:
        self.state.getActions().log(log)

    def getTeamLeeks(self, team: int):
        from ..state.entity import Entity
        leeks = []
        if team < len(self.state.getTeams()):
            for e in self.state.getTeams()[team].getEntities():
                if not e.isDead() and e.getType() == Entity.TYPE_LEEK:
                    leeks.append(e)
        return leeks

    def getTeamEntities(self, team: int):
        return self.state.getTeams()[team].getEntities()

    def getEntity(self, id_):
        return self.state.getEntity(id_)

    def _canStartFight(self) -> bool:
        if len(self.state.getTeams()) < 2:
            return False
        return True

    def startFight(self, drawCheckLife: bool) -> None:
        from ..fight.entity.entity_ai import EntityAI

        self.initFight()

        for entity in self.state.getEntities().values():
            # Build AI - in Python, ai_function comes from EntityInfo (already in entity.aiFile)
            ai_function = entity.getAIFile()  # Python AI function
            ai = EntityAI.build(self.generator, ai_function, entity)
            entity.setAI(ai)
            ai.setFight(self)

            # Check all entities characteristics
            self.state.statistics.init(entity)
            self.state.statistics.characteristics(entity)

            # Start fight for entity
            entity.startFight()

        # Run turns
        while self.state.getOrder().getTurn() <= self.max_turns and self.state.getState() == State.STATE_RUNNING:
            self.startTurn()
            if self.state.getOrder().current() is None:
                self.finishFight()
                break

        # Si match nul
        if self.state.getOrder().getTurn() == Fight.MAX_TURNS + 1:
            self.finishFight()

        # On supprime toutes les invocations
        entities = self.state.getAllEntities(True)
        for e in entities:
            if e.isSummon():
                self.state.removeInvocation(e, True)

        # Calcul de l'équipe gagnante
        self.computeWinner(drawCheckLife)

        self.state.statistics.endFight(list(self.state.getEntities().values()))
        if self.listener is not None:
            self.listener.newTurn(self)
        self.state.getActions().addOpsAndTimes(self.state.statistics)

    def computeWinner(self, drawCheckLife: bool) -> None:
        self.mWinteam = -1

        if self.state.getType() == State.TYPE_CHEST_HUNT:
            chestsAlive = False
            for team in self.state.getTeams():
                if team.containsChest() and team.isAlive():
                    chestsAlive = True
                    break
            if not chestsAlive:
                self.mWinteam = -2
            return

        alive = 0
        for t in range(len(self.state.getTeams())):
            if not self.state.getTeams()[t].isDead() and not self.state.getTeams()[t].containsChest():
                alive += 1
                self.mWinteam = t
        if alive != 1:
            self.mWinteam = -1
        if self.mWinteam == -1 and drawCheckLife:
            if self.state.getTeams()[0].getLife() > self.state.getTeams()[1].getLife():
                self.mWinteam = 0
            elif self.state.getTeams()[1].getLife() > self.state.getTeams()[0].getLife():
                self.mWinteam = 1

    def initFight(self) -> None:
        if len(self.state.getTeams()) < 2:
            raise FightException(FightException.NOT_ENOUGHT_PLAYERS)
        if self.state.getTeams()[0].size() == 0 or self.state.getTeams()[1].size() == 0:
            if self.state.getContext() == Fight.CONTEXT_TOURNAMENT:
                if self.state.getTeams()[0].size() == 0:
                    self.mWinteam = 1
                else:
                    self.mWinteam = 0
            raise FightException(FightException.NOT_ENOUGHT_PLAYERS)

        if not self._canStartFight():
            raise FightException(FightException.CANT_START_FIGHT)

        # Init the state
        self.state.init()

    def finishFight(self) -> None:
        self.state.setState(State.STATE_FINISHED)

    def startTurn(self) -> None:
        current = self.state.getOrder().current()
        if current is None:
            return

        self.state.getActions().log(ActionEntityTurn(current))
        if self.listener is not None:
            self.listener.newTurn(self)

        current.startTurn()

        if not current.isDead():
            ai = current.getAI()
            if ai is not None:
                if ai.isValid():
                    ai.setEntity(current)

                    startTime = time.perf_counter_ns()
                    ai.runTurn(self.state.getOrder().getTurn())
                    endTime = time.perf_counter_ns()

                    operations = getattr(ai, 'operations', 0)
                    if callable(operations):
                        operations = operations()
                    self.state.statistics.addTimes(current, endTime - startTime, operations)
                    self.executionTime += endTime - startTime
                    current.addOperations(operations)
                else:
                    self.log(ActionAIError(current))
                    self.state.statistics.error(current)
            current.endTurn()
            self.state.getActions().log(ActionEndTurn(current))
        self.state.endTurn()

    def useChip(self, caster, target, template) -> int:
        # Invocation but without AI: in Python, summons need an AI function
        if template.getAttack().getEffectParametersByType(Effect.TYPE_SUMMON) is not None:
            return self.summonEntity(caster, target, template, None)
        return self.state.useChip(caster, target, template)

    def summonEntity(self, caster, target, template, ai_function, name=None) -> int:
        from ..fight.entity.bulb_ai import BulbAI

        result = self.state.summonEntity(caster, target, template, name)

        if result > 0:
            summon = self.state.getLastEntity()
            summon.setFight(self)
            summon.setBirthTurn(self.getTurn())
            summon.setAI(BulbAI(summon, caster.getAI(), ai_function))

        return result

    def generateCritical(self, caster) -> bool:
        return self.state.getRandom().get_double() < (caster.getAgility() / 1000.0)

    def getTurn(self) -> int:
        return self.state.getOrder().getTurn()

    def getOrder(self):
        return self.state.getOrder()

    def setId(self, f: int) -> None:
        self.mId = f

    def setBoss(self, b: int) -> None:
        self.mBoss = b

    @staticmethod
    def getFightContext(type_: int) -> int:
        if type_ in (Fight.TYPE_SOLO_GARDEN, Fight.TYPE_TEAM_GARDEN, Fight.TYPE_FARMER_GARDEN):
            return Fight.CONTEXT_GARDEN
        elif type_ in (Fight.TYPE_SOLO_TEST, Fight.TYPE_TEAM_TEST, Fight.TYPE_FARMER_TEST):
            return Fight.CONTEXT_TEST
        elif type_ in (Fight.TYPE_TEAM_TOURNAMENT, Fight.TYPE_SOLO_TOURNAMENT, Fight.TYPE_FARMER_TOURNAMENT):
            return Fight.CONTEXT_TOURNAMENT
        elif type_ == Fight.FULL_TYPE_BATTLE_ROYALE:
            return Fight.CONTEXT_BATTLE_ROYALE
        return Fight.CONTEXT_CHALLENGE

    @staticmethod
    def getFightType(type_: int) -> int:
        if type_ in (Fight.TYPE_SOLO_GARDEN, Fight.TYPE_SOLO_CHALLENGE, Fight.TYPE_SOLO_TOURNAMENT, Fight.TYPE_SOLO_TEST):
            return Fight.TYPE_SOLO
        elif type_ in (Fight.TYPE_FARMER_GARDEN, Fight.TYPE_FARMER_TOURNAMENT, Fight.TYPE_FARMER_CHALLENGE, Fight.TYPE_FARMER_TEST):
            return Fight.TYPE_FARMER
        elif type_ == Fight.FULL_TYPE_BATTLE_ROYALE:
            return Fight.TYPE_BATTLE_ROYALE
        return Fight.TYPE_TEAM

    def setMaxTurns(self, max_turns: int) -> None:
        self.max_turns = max_turns

    def getDuration(self) -> int:
        return self.state.getOrder().getTurn()

    def getState(self):
        return self.state

    def setStatisticsManager(self, statisticsManager) -> None:
        self.state.setStatisticsManager(statisticsManager)
        statisticsManager.setGeneratorFight(self)
