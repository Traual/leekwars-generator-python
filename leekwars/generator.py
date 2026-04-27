"""Python port of Generator.

The main entry point of the generator. Loads game data (weapons, chips,
bulbs, components) at construction. Runs scenarios via runScenario.
The Python version uses Python AI functions instead of LeekScript.
"""

import os
import traceback

from . import log as Log
from .util import json_util as Json
from .util import util as Util
from .weapons.weapon import Weapon
from .weapons import weapons as Weapons
from .chips.chip import Chip
from .chips.chip_type import ChipType
from .chips import chips as Chips
from .bulbs.bulb_template import BulbTemplate
from .bulbs import bulbs as Bulbs
from .component.component import Component
from .component import components as Components
from .fight.fight import Fight
from .leek.farmer_log import FarmerLog
from .leek.leek_log import LeekLog
from .outcome.outcome import Outcome
from .state.entity import Entity
from .fight.entity.entity_ai import EntityAI


class Generator:

    TAG = "Generator"

    _errorManager = None

    def __init__(self, data_dir: str = None):
        self.use_leekscript_cache = True
        # Default: use the JSON files bundled inside the package, so the
        # engine works after `pip install` regardless of cwd.
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "_data")
        self.data_dir = data_dir
        os.makedirs("ai/", exist_ok=True)
        self._loadWeapons()
        self._loadChips()
        self._loadSummons()
        self._loadComponents()

    def runScenario(self, scenario, listener, registerManager, statisticsManager) -> Outcome:
        outcome = Outcome()

        fight = Fight(self, listener)
        fight.getState().setRegisterManager(registerManager)
        fight.setStatisticsManager(statisticsManager)
        fight.setId(scenario.fightID)
        fight.setBoss(scenario.boss)
        fight.setMaxTurns(scenario.maxTurns)
        fight.getState().setType(scenario.type)
        fight.getState().setContext(scenario.context)
        fight.getState().setCustomMap(scenario.map)
        fight.getState().seed(scenario.seed)

        # Create logs and compile AIs
        t = 0
        for team in scenario.entities:
            for entityInfo in team:
                # Create farmer logs
                aiOwner = entityInfo.aiOwner
                if entityInfo.type == Entity.TYPE_MOB:
                    aiOwner = 0
                if aiOwner not in outcome.logs:
                    outcome.logs[aiOwner] = FarmerLog(fight, entityInfo.farmer)

                # Create entity
                entity = entityInfo.createEntity(self, scenario, fight)
                fight.getState().addEntity(t, entity)
                entity.setFight(fight)
                entity.setBirthTurn(1)

                # Resolve AI - in Python version this is just the AI function from EntityInfo
                entity.setLogs(LeekLog(outcome.logs[aiOwner], entity))
                entity.setAIFile(EntityAI.resolve(self, entityInfo, entity))
            t += 1

        try:
            fight.startFight(scenario.drawCheckLife)
            fight.finishFight()

            outcome.fight = fight.getState().getActions()
            outcome.fight.dead = fight.getState().getDeadReport()
            outcome.winner = fight.getWinner()
            outcome.duration = fight.getState().getDuration()
            outcome.statistics = statisticsManager
            for entity in fight.getState().getEntities().values():
                if entity.getAI() is not None:
                    outcome.analyzeTime += entity.getAI().getAnalyzeTime()
                    outcome.compilationTime += entity.getAI().getCompileTime()
            outcome.executionTime = fight.executionTime

            # Save registers
            for entity in fight.getState().getEntities().values():
                if not entity.isSummon() and entity.getRegisters() is not None and (entity.getRegisters().isModified() or entity.getRegisters().isNew()):
                    registerManager.saveRegisters(entity.getId(), entity.getRegisters().toJSONString(), entity.getRegisters().isNew())
            return outcome

        except Exception as e:
            outcome.exception = e
            traceback.print_exc()
            return outcome

    def _loadWeapons(self) -> None:
        try:
            content = Util.read_file(os.path.join(self.data_dir, "weapons.json"))
            weapons = Json.parse_object(content)
            for id_, weapon in weapons.items():
                # Normalize: data files may omit max_uses and may store los as int 0/1
                effects = self._normalizeEffects(weapon.get("effects", []))
                passive = self._normalizeEffects(weapon.get("passive_effects", []))
                Weapons.addWeapon(Weapon(
                    weapon["item"], weapon["cost"],
                    weapon["min_range"], weapon["max_range"],
                    effects,
                    int(weapon["launch_type"]), int(weapon["area"]),
                    bool(weapon.get("los", True)), weapon["template"], weapon["name"],
                    passive, weapon.get("max_uses", -1)))
        except Exception as e:
            print("Error loading weapons:", e)
            traceback.print_exc()

    def _loadChips(self) -> None:
        try:
            content = Util.read_file(os.path.join(self.data_dir, "chips.json"))
            chips = Json.parse_object(content)
            for id_, chip in chips.items():
                effects = self._normalizeEffects(chip.get("effects", []))
                Chips.addChip(Chip(
                    int(id_), chip["cost"],
                    chip["min_range"], chip["max_range"],
                    effects,
                    int(chip["launch_type"]), int(chip["area"]),
                    bool(chip.get("los", True)), chip["cooldown"],
                    bool(chip.get("team_cooldown", False)), chip["initial_cooldown"],
                    chip["level"], chip["template"], chip["name"],
                    list(ChipType)[chip["type"]], chip.get("max_uses", -1)))
        except Exception as e:
            print("Error loading chips:", e)
            traceback.print_exc()

    @staticmethod
    def _normalizeEffects(effects):
        """Ensure each effect dict has all expected keys."""
        result = []
        for e in effects:
            result.append({
                "id": e.get("id", e.get("type", 0)),
                "value1": e.get("value1", 0),
                "value2": e.get("value2", 0),
                "turns": e.get("turns", 0),
                "targets": e.get("targets", 0),
                "modifiers": e.get("modifiers", 0),
            })
        return result

    def _loadSummons(self) -> None:
        try:
            content = Util.read_file(os.path.join(self.data_dir, "summons.json"))
            summons = Json.parse_object(content)
            for id_, summon in summons.items():
                Bulbs.addInvocationTemplate(BulbTemplate(
                    int(id_), summon["name"],
                    summon["chips"], summon["characteristics"]))
        except Exception as e:
            print("Error loading summons:", e)
            traceback.print_exc()

    def _loadComponents(self) -> None:
        try:
            content = Util.read_file(os.path.join(self.data_dir, "components.json"))
            components = Json.parse_object(content)
            for id_, component in components.items():
                Components.addComponent(Component(
                    int(id_), component["name"],
                    component["stats"], component["template"]))
        except Exception as e:
            print("Error loading components:", e)
            traceback.print_exc()

    def setCache(self, cache: bool) -> None:
        self.use_leekscript_cache = cache

    @classmethod
    def setErrorManager(cls, manager) -> None:
        cls._errorManager = manager

    def exception(self, e, fight=None, farmer=None, file=None) -> None:
        if Generator._errorManager is not None:
            if fight is None:
                Generator._errorManager.exception(e, -1)
            elif farmer is None:
                Generator._errorManager.exception(e, fight.getId())
            else:
                Generator._errorManager.exception(e, fight.getId(), farmer, file)
