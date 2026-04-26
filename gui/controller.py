"""Interactive fight controller for the GUI.

Wraps a Fight so the human player's turn pauses for input. The opposing AI
runs as a normal Python AI between player turns.
"""

import os
import random
import sys

# Make leekwars/ importable when run from gui/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import leekwars.effect  # populate Effect.effects
from leekwars.generator import Generator
from leekwars.scenario.scenario import Scenario
from leekwars.scenario.farmer_info import FarmerInfo
from leekwars.scenario.team_info import TeamInfo
from leekwars.scenario.entity_info import EntityInfo
from leekwars.statistics.statistics_manager import DefaultStatisticsManager
from leekwars.fight.fight import Fight
from leekwars.state.state import State
from leekwars.leek.register_manager import RegisterManager
from leekwars.leek.farmer_log import FarmerLog
from leekwars.leek.leek_log import LeekLog
from leekwars.fight.entity.entity_ai import EntityAI
from leekwars.action.action_entity_turn import ActionEntityTurn
from leekwars.action.action_end_turn import ActionEndTurn
from leekwars.action.action_ai_error import ActionAIError
from leekwars.weapons import weapons as Weapons
from leekwars.classes import fight_class, entity_class, weapon_class


# Some good 1v1-friendly weapons (single or low-AOE).
WEAPON_POOL = [37, 38, 39, 41, 45, 42, 43, 47, 60, 151, 153, 175, 180, 184, 277, 278]


class _Stats(DefaultStatisticsManager):
    def setGeneratorFight(self, fight):
        self._fight = fight


class _Reg(RegisterManager):
    def getRegisters(self, leek):
        return None
    def saveRegisters(self, leek, registers, is_new):
        pass


def _basic_ai(ai):
    weapons = entity_class.getWeapons(ai)
    if weapons:
        entity_class.setWeapon(ai, weapons[0])
    enemy = fight_class.getNearestEnemy(ai)
    fight_class.moveToward(ai, enemy)
    if enemy >= 0:
        try:
            weapon_class.useWeapon(ai, enemy)
        except Exception:
            pass


def _player_ai(ai):
    """Placeholder — never executed; the GUI controller runs player turns by hand."""
    return


def _make_random_scenario(seed: int, player_team: int) -> Scenario:
    rng = random.Random(seed)
    scenario = Scenario()
    scenario.seed = seed
    scenario.maxTurns = 64
    scenario.type = State.TYPE_SOLO
    scenario.context = State.CONTEXT_TEST

    f1 = FarmerInfo(); f1.id = 1; f1.name = "You"; f1.country = "fr"
    f2 = FarmerInfo(); f2.id = 2; f2.name = "Bot"; f2.country = "fr"
    scenario.farmers[1] = f1
    scenario.farmers[2] = f2

    t1 = TeamInfo(); t1.id = 1; t1.name = "Yours"
    t2 = TeamInfo(); t2.id = 2; t2.name = "Bots"
    scenario.teams[1] = t1
    scenario.teams[2] = t2

    def make_entity(eid, team_id, farmer_id, name, ai_function):
        e = EntityInfo()
        e.id = eid
        e.name = name
        e.type = 0  # Leek
        e.farmer = farmer_id
        e.team = team_id
        e.level = rng.randint(80, 200)
        e.life = rng.randint(2000, 4500)
        e.strength = rng.randint(150, 400)
        e.agility = rng.randint(0, 200)
        e.wisdom = rng.randint(0, 100)
        e.resistance = rng.randint(0, 200)
        e.science = rng.randint(0, 100)
        e.magic = rng.randint(0, 100)
        e.frequency = rng.randint(50, 150)
        e.cores = 10
        e.ram = 10
        e.tp = rng.randint(12, 18)
        e.mp = rng.randint(5, 8)
        # 1-2 random weapons from the pool
        weapon_count = rng.randint(1, 2)
        e.weapons = rng.sample(WEAPON_POOL, weapon_count)
        e.chips = []
        e.ai_function = ai_function
        return e

    player_entity = make_entity(1, 1, 1, "Player", _player_ai)
    bot_entity = make_entity(2, 2, 2, "Bot", _basic_ai)

    if player_team == 0:
        scenario.addEntity(0, player_entity)
        scenario.addEntity(1, bot_entity)
    else:
        scenario.addEntity(0, bot_entity)
        scenario.addEntity(1, player_entity)
    return scenario


class FightController:
    """One interactive fight. Not thread-safe; one per session."""

    def __init__(self, generator: Generator, seed: int):
        self.seed = seed
        self.scenario = _make_random_scenario(seed, player_team=0)
        self.generator = generator

        self.fight = Fight(generator, listener=None)
        state = self.fight.getState()
        state.setRegisterManager(_Reg())
        self.fight.setStatisticsManager(_Stats())
        self.fight.setId(1)
        self.fight.setMaxTurns(self.scenario.maxTurns)
        state.setType(self.scenario.type)
        state.setContext(self.scenario.context)
        state.seed(self.scenario.seed)

        outcome_logs = {}
        t = 0
        for team in self.scenario.entities:
            for entity_info in team:
                if entity_info.aiOwner not in outcome_logs:
                    outcome_logs[entity_info.aiOwner] = FarmerLog(self.fight, entity_info.farmer)
                entity = entity_info.createEntity(generator, self.scenario, self.fight)
                state.addEntity(t, entity)
                entity.setFight(self.fight)
                entity.setBirthTurn(1)
                entity.setLogs(LeekLog(outcome_logs[entity_info.aiOwner], entity))
                entity.setAIFile(EntityAI.resolve(generator, entity_info, entity))
            t += 1

        self.fight.initFight()
        for entity in state.getEntities().values():
            ai_function = entity.getAIFile()
            ai = EntityAI.build(generator, ai_function, entity)
            entity.setAI(ai)
            ai.setFight(self.fight)
            state.statistics.init(entity)
            state.statistics.characteristics(entity)
            entity.startFight()

        # Identify the player entity (the one whose ai_function is _player_ai)
        self.player_entity = None
        for entity in state.getEntities().values():
            if entity.getAIFile() is _player_ai:
                self.player_entity = entity
                break

        self.finished = False
        self.winner = None
        self._action_index = 0  # index into actions for incremental delivery

        # Auto-advance until it's player's turn (or fight ends)
        self._advance_to_player_turn()

    # ---- Turn engine -----------------------------------------------------

    def _is_player_turn(self) -> bool:
        if self.finished:
            return False
        current = self.fight.getState().getOrder().current()
        return current is self.player_entity

    def _advance_to_player_turn(self):
        """Run AI turns until it's the player's turn, the fight ends, or the player is dead."""
        state = self.fight.getState()
        guard = 0
        while not self.finished and not self._is_player_turn():
            guard += 1
            if guard > 256:
                # Safety net: shouldn't happen, but avoid infinite loops
                break
            current = state.getOrder().current()
            if current is None:
                self._finish_fight()
                break
            if state.getState() != State.STATE_RUNNING:
                self._finish_fight()
                break

            # Run one turn for current AI entity
            state.getActions().log(ActionEntityTurn(current))
            current.startTurn()
            if not current.isDead():
                ai = current.getAI()
                if ai is not None and ai.isValid():
                    try:
                        ai.runTurn(state.getOrder().getTurn())
                    except Exception:
                        self.fight.log(ActionAIError(current))
                current.endTurn()
                state.getActions().log(ActionEndTurn(current))
            state.endTurn()

            if state.getState() == State.STATE_FINISHED:
                self._finish_fight()
                break

    def _start_player_turn_log(self):
        """Log the LEEK_TURN action for the player, called once when their turn begins."""
        state = self.fight.getState()
        # Look for a LEEK_TURN action at the current position in actions, or add one
        # We always log it here to mirror how Fight.startTurn does it
        # But avoid duplicate: only log if last action isn't already this LEEK_TURN
        actions = state.getActions().actions
        # The previous turn ended with [END_TURN, ...] or [NEW_TURN, ...]; log LEEK_TURN now
        from leekwars.action.action import Action as A
        if not actions or actions[-1].getJSON()[0] != A.LEEK_TURN or actions[-1].getJSON()[1] != self.player_entity.getFId():
            state.getActions().log(ActionEntityTurn(self.player_entity))
        self.player_entity.startTurn()

    _player_turn_started = False

    def _ensure_player_turn_started(self):
        if not self._player_turn_started and self._is_player_turn() and not self.finished:
            self._start_player_turn_log()
            self._player_turn_started = True

    def end_player_turn(self):
        if not self._is_player_turn() or self.finished:
            return
        state = self.fight.getState()
        if not self.player_entity.isDead():
            self.player_entity.endTurn()
            state.getActions().log(ActionEndTurn(self.player_entity))
        state.endTurn()
        self._player_turn_started = False
        if state.getState() == State.STATE_FINISHED:
            self._finish_fight()
        else:
            self._advance_to_player_turn()

    def _finish_fight(self):
        if self.finished:
            return
        self.finished = True
        self.fight.computeWinner(False)
        self.winner = self.fight.getWinner()
        self.fight.finishFight()

    # ---- Player actions --------------------------------------------------

    def player_set_weapon(self, weapon_id: int) -> bool:
        if not self._is_player_turn() or self.finished:
            return False
        self._ensure_player_turn_started()
        weapon = Weapons.getWeapon(weapon_id)
        if weapon is None or not self.player_entity.hasWeapon(weapon_id):
            return False
        return self.fight.getState().setWeapon(self.player_entity, weapon)

    def player_move_to(self, cell_id: int) -> int:
        if not self._is_player_turn() or self.finished:
            return 0
        self._ensure_player_turn_started()
        state = self.fight.getState()
        target = state.getMap().getCell(cell_id)
        if target is None or not target.isWalkable() or target.getPlayer(state.getMap()) is not None:
            return 0
        path = state.getMap().getPathBeetween(self.player_entity.getCell(), target, None)
        if not path:
            return 0
        max_pm = self.player_entity.getMP()
        if max_pm <= 0:
            return 0
        return state.moveEntity(self.player_entity, path[:max_pm])

    def player_use_weapon(self, target_cell_id: int) -> int:
        if not self._is_player_turn() or self.finished:
            return 0
        self._ensure_player_turn_started()
        state = self.fight.getState()
        target = state.getMap().getCell(target_cell_id)
        if target is None:
            return 0
        return state.useWeapon(self.player_entity, target)

    # ---- State serialization --------------------------------------------

    def _entity_dict(self, entity):
        return {
            "id": entity.getFId(),
            "name": entity.getName(),
            "team": entity.getTeam(),
            "hp": entity.getLife(),
            "max_hp": entity.getTotalLife(),
            "tp": entity.getTP(),
            "max_tp": entity.getTotalTP(),
            "mp": entity.getMP(),
            "max_mp": entity.getTotalMP(),
            "strength": entity.getStrength(),
            "agility": entity.getAgility(),
            "wisdom": entity.getWisdom(),
            "resistance": entity.getResistance(),
            "science": entity.getScience(),
            "magic": entity.getMagic(),
            "frequency": entity.getFrequency(),
            "cell": entity.getCell().getId() if entity.getCell() is not None else None,
            "weapons": [w.getId() for w in entity.getWeapons()],
            "current_weapon": entity.getWeapon().getId() if entity.getWeapon() is not None else None,
            "alive": entity.isAlive(),
            "is_player": entity is self.player_entity,
        }

    def get_state_dict(self):
        self._ensure_player_turn_started()
        state = self.fight.getState()
        m = state.getMap()
        cells = []
        for c in m.getCells():
            cells.append({
                "id": c.getId(),
                "x": c.getX(),
                "y": c.getY(),
                "walkable": c.isWalkable(),
                "obstacle": c.getObstacle() if not c.isWalkable() else 0,
            })
        weapons_meta = {}
        for entity in state.getEntities().values():
            for w in entity.getWeapons():
                if w.getId() not in weapons_meta:
                    weapons_meta[w.getId()] = {
                        "id": w.getId(),
                        "name": w.getName(),
                        "min_range": w.getAttack().getMinRange(),
                        "max_range": w.getAttack().getMaxRange(),
                        "cost": w.getCost(),
                        "los": w.getAttack().needLos(),
                        "launch_type": w.getAttack().getLaunchType(),
                        "area": w.getAttack().getArea(),
                    }
        # Reachable cells from the player's current cell (within MP)
        reachable = []
        attackable = []
        if self._is_player_turn() and not self.finished and self.player_entity.getCell() is not None:
            mp = self.player_entity.getMP()
            origin = self.player_entity.getCell()
            if mp > 0:
                for c in m.getCells():
                    if not c.isWalkable() or c is origin or c.getPlayer(m) is not None:
                        continue
                    path = m.getPathBeetween(origin, c, None)
                    if path is not None and 0 < len(path) <= mp:
                        reachable.append(c.getId())
            weapon = self.player_entity.getWeapon()
            if weapon is not None and self.player_entity.getTP() >= weapon.getCost():
                for c in m.getCells():
                    if m.canUseAttack(self.player_entity.getCell(), c, weapon.getAttack()):
                        attackable.append(c.getId())
        return {
            "seed": self.seed,
            "turn": state.getOrder().getTurn(),
            "current_entity": state.getOrder().current().getFId() if state.getOrder().current() else None,
            "player_entity_id": self.player_entity.getFId(),
            "is_player_turn": self._is_player_turn(),
            "finished": self.finished,
            "winner": self.winner,
            "map_width": m.getWidth(),
            "map_height": m.getHeight(),
            "min_x": m.min_x,
            "max_x": m.max_x,
            "min_y": m.min_y,
            "max_y": m.max_y,
            "cells": cells,
            "entities": [self._entity_dict(e) for e in state.getEntities().values()],
            "weapons": list(weapons_meta.values()),
            "reachable_cells": reachable,
            "attackable_cells": attackable,
            "log": self._actions_since_last(),
        }

    def _actions_since_last(self):
        actions = self.fight.getState().getActions().actions
        new = []
        for i in range(self._action_index, len(actions)):
            new.append(actions[i].getJSON())
        self._action_index = len(actions)
        return new
