import datetime
import math

from .order import Order
from .start_order import StartOrder
from .team import Team
from .entity import Entity
from ..util.random_generator import RandomGenerator
from ..action.actions import Actions
from ..attack.attack import Attack
from ..action.action_use_weapon import ActionUseWeapon
from ..action.action_use_chip import ActionUseChip
from ..action.action_invocation import ActionInvocation


from ..util.java_math import java_long as _java_long_overflow, java_div as _java_div, java_mod as _java_mod


class _DefaultRandom(RandomGenerator):
    """Default RandomGenerator matching Java's deterministic linear congruential implementation."""

    def __init__(self):
        self.n = 0

    def seed(self, seed):
        self.n = _java_long_overflow(seed)

    def get_double(self) -> float:
        # n = n * 1103515245 + 12345 in signed 64-bit long
        self.n = _java_long_overflow(self.n * 1103515245 + 12345)
        # r = (n / 65536) % 32768 + 32768 — Java long division truncates toward zero
        r = _java_mod(_java_div(self.n, 65536), 32768) + 32768
        return r / 65536.0

    def get_int(self, min_v: int, max_v: int) -> int:
        if max_v - min_v + 1 <= 0:
            return 0
        return min_v + int(self.get_double() * (max_v - min_v + 1))

    def get_long(self, min_v: int, max_v: int) -> int:
        if max_v - min_v + 1 <= 0:
            return 0
        return min_v + int(self.get_double() * (max_v - min_v + 1))


class State:

    TAG = "State"

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
    FULL_TYPE_WAR_GARDEN = 20
    FULL_TYPE_WAR_AUTO = 21
    FULL_TYPE_CHEST_HUNT_GARDEN = 22
    FULL_TYPE_CHEST_HUNT_AUTO = 23
    FULL_TYPE_COLOSSUS_GARDEN = 24
    FULL_TYPE_COLOSSUS_AUTO = 25

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
    TYPE_WAR = 5
    TYPE_CHEST_HUNT = 6
    TYPE_COLOSSUS = 7

    # Summon limit
    SUMMON_LIMIT = 8

    MAX_TURNS = 64

    # Fight states
    STATE_INIT = 0
    STATE_RUNNING = 1
    STATE_FINISHED = 2

    def __init__(self, other=None):
        if other is not None:
            self._init_copy(other)
            return

        self.randomGenerator = _DefaultRandom()
        self.teams = []
        self.initialOrder = []
        self.mNextEntityId = 0
        self.mWinteam = -1
        self.mEntities = {}
        self.mId = 0
        self.mState = State.STATE_INIT
        self.order = None
        self.fullType = State.TYPE_SOLO_GARDEN
        self.mStartFarmer = -1
        self.lastTurn = 0
        self.colossusMultiplier = 0
        self.date = datetime.datetime.now()
        self.map = None
        self.actions = Actions()
        self.mLeekDatas = ""
        self.context = State.CONTEXT_GARDEN
        self.type = State.TYPE_SOLO
        self.custom_map = None
        self.statistics = None
        self.registerManager = None
        self.executionTime = 0
        self.seed_val = 0

    def _init_copy(self, state):
        from ..leek.leek import Leek
        from ..maps.map import Map
        self.mId = state.mId
        self.mState = state.mState
        self.actions = Actions()
        self.randomGenerator = state.randomGenerator

        self.mEntities = {}
        for key, entity in state.mEntities.items():
            newEntity = Leek(entity)
            newEntity.setState(self, entity.getFId())
            self.mEntities[key] = newEntity

        # Effets
        for entity in self.mEntities.values():
            for effet in state.mEntities[entity.getFId()].effects:
                newEffect = effet.clone()
                caster = self.mEntities[newEffect.getCaster().getFId()]
                newEffect.setTarget(entity)
                newEffect.setCaster(caster)
                entity.addEffect(newEffect)
                caster.addLaunchedEffect(newEffect)

        self.initialOrder = []
        for entity in state.initialOrder:
            self.initialOrder.append(self.mEntities[entity.getFId()])
        self.order = Order(state.order, self)
        self.teams = []
        for team in state.teams:
            self.teams.append(Team(team, self))

        self.map = Map.copy(state.map, self)

        self.statistics = state.statistics
        self.registerManager = state.registerManager
        self.fullType = state.fullType
        self.type = state.type
        self.context = state.context
        self.mNextEntityId = state.mNextEntityId
        self.mWinteam = state.mWinteam
        self.mStartFarmer = state.mStartFarmer
        self.lastTurn = state.lastTurn
        self.date = state.date
        self.mLeekDatas = state.mLeekDatas
        self.executionTime = state.executionTime
        self.seed_val = state.seed_val
        self.colossusMultiplier = 0
        self.custom_map = None

    def addFlag(self, team: int, flag: int) -> None:
        self.teams[team].addFlag(flag)

    def getFlags(self, team: int):
        return self.teams[team].getFlags()

    def getWinner(self) -> int:
        return self.mWinteam

    def setTeamID(self, team: int, id_: int) -> None:
        if team < len(self.teams):
            self.teams[team].setID(id_)

    def getEntities(self):
        return self.mEntities

    def setStartFarmer(self, startFarmer: int) -> None:
        self.mStartFarmer = startFarmer

    def getStartFarmer(self) -> int:
        return self.mStartFarmer

    def getTeamID(self, team: int) -> int:
        if team < len(self.teams):
            return self.teams[team].getID()
        return -1

    def getId(self) -> int:
        return self.mId

    def getLeekDatas(self) -> str:
        return self.mLeekDatas

    def log(self, log) -> None:
        self.actions.log(log)

    def getMap(self):
        return self.map

    def setCustomMap(self, map_) -> None:
        self.custom_map = map_

    def addEntity(self, t: int, entity) -> None:
        if entity is None or t < 0:
            return

        team = t
        if self.type == State.TYPE_BATTLE_ROYALE:
            team = len(self.teams)

        while len(self.teams) < team + 1:
            self.teams.append(Team())

        entity.setTeam(team)
        self.teams[team].addEntity(entity)
        entity.setState(self, self.getNextEntityId())
        self.mEntities[entity.getFId()] = entity

    def getEnemiesEntities(self, team: int, get_deads: bool = False):
        enemies = []
        for t in range(len(self.teams)):
            if t != team:
                enemies.extend(self.getTeamEntities(t, get_deads))
        return enemies

    def getTeamLeeks(self, team: int):
        leeks = []
        if team < len(self.teams):
            for e in self.teams[team].getEntities():
                if not e.isDead() and e.getType() == Entity.TYPE_LEEK:
                    leeks.append(e)
        return leeks

    def getTeamEntities(self, team: int, dead: bool = False):
        leeks = []
        if team < len(self.teams):
            for e in self.teams[team].getEntities():
                if dead or not e.isDead():
                    leeks.append(e)
        return leeks

    def getAllEntities(self, get_deads: bool):
        leeks = []
        for t in self.teams:
            for e in t.getEntities():
                if get_deads or not e.isDead():
                    leeks.append(e)
        return leeks

    def getEntity(self, id_):
        return self.mEntities.get(int(id_))

    def computeWinner(self, drawCheckLife: bool) -> None:
        self.mWinteam = -1

        if self.type == State.TYPE_CHEST_HUNT:
            chestsAlive = False
            for team in self.teams:
                if team.containsChest() and team.isAlive():
                    chestsAlive = True
                    break
            if not chestsAlive:
                self.mWinteam = -2
            return

        alive = 0
        for t in range(len(self.teams)):
            if not self.teams[t].isDead() and not self.teams[t].containsChest():
                alive += 1
                self.mWinteam = t
        if alive != 1:
            self.mWinteam = -1
        if self.mWinteam == -1 and drawCheckLife:
            if self.teams[0].getLife() > self.teams[1].getLife():
                self.mWinteam = 0
            elif self.teams[1].getLife() > self.teams[0].getLife():
                self.mWinteam = 1

    def init(self) -> None:
        from ..maps.map import Map
        from ..action.action_start_fight import ActionStartFight
        from ..chips import chips as Chips
        from ..effect.effect import Effect

        # Create level/skin list
        list_ = {}
        for l in self.mEntities.values():
            data = []
            data.append(l.getLevel())
            data.append(l.getSkin())
            if l.getHat() > 0:
                data.append(l.getHat())
            else:
                data.append(None)
            list_[str(l.getId())] = data

        from ..util import json_util as Json
        self.mLeekDatas = Json.to_json(list_)

        obstacle_count = self.getRandom().get_int(30, 80)

        self.map = Map.generateMap(self, self.context, 18, 18, obstacle_count, self.teams, self.custom_map)

        # Initialize positions and game order
        bootorder = StartOrder()
        self.order = Order()

        for t in self.teams:
            for e in t.getEntities():
                bootorder.addEntity(e)

        for e in bootorder.compute(self):
            if e.isAlive():
                self.order.addEntity(e)
            self.actions.addEntity(e, False)
            self.initialOrder.append(e)

            # Coffre ?
            if e.getType() == Entity.TYPE_CHEST:
                self.statistics.chest()

        # On ajoute la map
        self.actions.addMap(self.map)

        # Cooldowns initiaux
        for chip_id, chip in Chips.getTemplates().items():
            if chip.getInitialCooldown() > 0:
                for t in self.teams:
                    for entity in t.getEntities():
                        self.addCooldown(entity, chip, chip.getInitialCooldown() + 1)

        # Puis on ajoute le startfight
        self.actions.log(ActionStartFight(self.teams[0].size(), self.teams[1].size() if len(self.teams) > 1 else 0))

        # Colossus: apply initial x3 multiply stats effect on team 2
        if self.type == State.TYPE_COLOSSUS and len(self.teams) > 1:
            self.colossusMultiplier = 3
            for e in self.teams[1].getEntities():
                Effect.createEffect(self, Effect.TYPE_MULTIPLY_STATS, -1, 1, self.colossusMultiplier, 0, False, e, e, None, 0, False, 0, 1, 0, Effect.MODIFIER_IRREDUCTIBLE)

        self.mState = State.STATE_RUNNING

    def startTurn(self):
        from ..action.action_entity_turn import ActionEntityTurn
        from ..action.action_end_turn import ActionEndTurn

        current = self.order.current()
        if current is None:
            return

        self.actions.log(ActionEntityTurn(current))
        current.startTurn()

        if not current.isDead():
            current.endTurn()
            self.actions.log(ActionEndTurn(current))
        self.endTurn()

    def onPlayerDie(self, entity, killer, item) -> None:
        from ..action.action_entity_die import ActionEntityDie
        from ..action.action_chest_opened import ActionChestOpened
        from ..effect.effect import Effect

        killCell = entity.getCell()

        self.order.removeEntity(entity)
        self.map.removeEntity(entity)

        self.actions.log(ActionEntityDie(entity, killer))
        self.statistics.kill(killer, entity, item, killCell)

        # BR : give 10 (or 2 for bulb) power + 50% of power to the killer
        if self.type == State.TYPE_BATTLE_ROYALE and killer is not None:
            amount = 2 if entity.isSummon() else 10
            existing_effect = None
            for e in entity.getEffects():
                if e.getAttack() is None and e.getID() == Effect.TYPE_RAW_BUFF_POWER:
                    existing_effect = e
                    break
            if existing_effect is not None:
                amount += int(existing_effect.value / 2)
            Effect.createEffect(self, Effect.TYPE_RAW_BUFF_POWER, -1, 1, amount, 0, False, killer, killer, None, 0, True, 0, 1, 0, Effect.MODIFIER_IRREDUCTIBLE)

        # Coffre ouvert
        if entity.getType() == Entity.TYPE_CHEST and entity.getResurrected() == 0:
            if self.context != State.CONTEXT_CHALLENGE:
                resources = entity.loot(self)
                self.actions.log(ActionChestOpened(killer, entity, resources))
                self.statistics.chestKilled(killer, entity, resources)

            amount = 10 if entity.getLevel() == 100 else (50 if entity.getLevel() == 200 else 100)
            Effect.createEffect(self, Effect.TYPE_RAW_BUFF_POWER, -1, 1, amount, 0, False, killer, killer, None, 0, True, 0, 1, 0, Effect.MODIFIER_IRREDUCTIBLE)

        # Passive effect ally killed
        if not entity.isSummon():
            for ally in self.getTeamEntities(entity.getTeam()):
                if ally is entity:
                    continue
                ally.onAllyKilled()

        # Passive effect kill
        if killer is not None:
            killer.onKill()

    def isFinished(self) -> bool:
        if self.type == State.TYPE_CHEST_HUNT:
            for team in self.teams:
                if team.containsChest() and team.isAlive():
                    return False
            return True

        aliveTeams = 0
        for team in self.teams:
            if team.isAlive() and not team.containsChest():
                aliveTeams += 1
                if aliveTeams >= 2:
                    return False
        return True

    def endTurn(self) -> None:
        from ..action.action_new_turn import ActionNewTurn
        from ..effect.effect import Effect

        if self.isFinished():
            self.mState = State.STATE_FINISHED
        else:
            if self.order.next():
                if self.lastTurn != self.order.getTurn() and self.order.getTurn() <= State.MAX_TURNS:
                    self.actions.log(ActionNewTurn(self.order.getTurn()))
                    self.lastTurn = self.order.getTurn()

                    if self.type == State.TYPE_BATTLE_ROYALE:
                        self.giveBRPower()
                    if self.type == State.TYPE_COLOSSUS and len(self.teams) > 1 and self.order.getTurn() % 5 == 1:
                        self.colossusMultiplier += 1
                        for e in self.teams[1].getEntities():
                            if not e.isDead():
                                Effect.createEffect(self, Effect.TYPE_MULTIPLY_STATS, -1, 1, self.colossusMultiplier, 0, False, e, e, None, 0, False, 0, 1, 0, Effect.MODIFIER_IRREDUCTIBLE)

                for t in self.teams:
                    t.applyCoolDown()

    def giveBRPower(self) -> None:
        from ..effect.effect import Effect
        power = 2
        for entity in self.getAllEntities(False):
            Effect.createEffect(self, Effect.TYPE_RAW_BUFF_POWER, -1, 1, power, 0, False, entity, entity, None, 0, True, 0, 1, 0, Effect.MODIFIER_IRREDUCTIBLE)

    def setWeapon(self, entity_or_id, weapon) -> bool:
        from ..action.action_set_weapon import ActionSetWeapon
        if not isinstance(entity_or_id, Entity):
            entity = self.getEntity(entity_or_id)
        else:
            entity = entity_or_id
        # 1 TP required
        if entity.getTP() <= 0:
            return False
        entity.setWeapon(weapon)
        entity.useTP(1)
        self.log(ActionSetWeapon(weapon))
        self.statistics.setWeapon(entity, weapon)
        return True

    def useWeapon(self, launcher_or_id, target_or_id) -> int:
        if not isinstance(launcher_or_id, Entity):
            launcher = self.getEntity(launcher_or_id)
            target = self.getMap().getCell(target_or_id)
        else:
            launcher = launcher_or_id
            target = target_or_id

        if self.order.current() is not launcher or launcher.getWeapon() is None:
            return Attack.USE_INVALID_TARGET

        weapon = launcher.getWeapon()

        # Coût
        if weapon.getCost() > launcher.getTP():
            return Attack.USE_NOT_ENOUGH_TP

        # Nombre d'utilisations par tour
        if weapon.getAttack().getMaxUses() != -1 and launcher.getItemUses(weapon.getId()) >= weapon.getAttack().getMaxUses():
            return Attack.USE_MAX_USES

        # Position
        if not self.map.canUseAttack(launcher.getCell(), target, weapon.getAttack()):
            return Attack.USE_INVALID_POSITION

        critical = self.generateCritical(launcher)
        result = Attack.USE_CRITICAL if critical else Attack.USE_SUCCESS

        cellEntity = target.getPlayer(self.map)
        log_use = ActionUseWeapon(target, result)
        self.actions.log(log_use)
        if critical:
            launcher.onCritical()
        target_leeks = weapon.getAttack().applyOnCell(self, launcher, target, critical)
        self.statistics.useWeapon(launcher, weapon, target, target_leeks, cellEntity)
        if critical:
            self.statistics.critical(launcher)

        launcher.useTP(weapon.getCost())
        launcher.addItemUse(weapon.getId())

        return result

    def useChip(self, caster_or_id, target_or_id, template) -> int:
        from ..effect.effect import Effect
        if not isinstance(caster_or_id, Entity):
            caster = self.getEntity(caster_or_id)
            target = self.getMap().getCell(target_or_id)
        else:
            caster = caster_or_id
            target = target_or_id

        if self.order.current() is not caster:
            return Attack.USE_INVALID_TARGET
        if template.getCost() > 0 and template.getCost() > caster.getTP():
            return Attack.USE_NOT_ENOUGH_TP
        if self.hasCooldown(caster, template):
            return Attack.USE_INVALID_COOLDOWN
        if template.getAttack().getMaxUses() != -1 and caster.getItemUses(template.getId()) >= template.getAttack().getMaxUses():
            return Attack.USE_MAX_USES
        if not target.isWalkable() or not self.map.canUseAttack(caster.getCell(), target, template.getAttack()):
            self.statistics.useInvalidPosition(caster, template.getAttack(), target)
            return Attack.USE_INVALID_POSITION

        for parameters in template.getAttack().getEffects():
            if parameters.getId() == Effect.TYPE_TELEPORT and not target.available(self.map):
                return Attack.USE_INVALID_TARGET

        critical = self.generateCritical(caster)
        result = Attack.USE_CRITICAL if critical else Attack.USE_SUCCESS

        cellEntity = target.getPlayer(self.map)
        log = ActionUseChip(target, template, result)
        self.actions.log(log)
        if critical:
            caster.onCritical()
        targets = template.getAttack().applyOnCell(self, caster, target, critical)
        self.statistics.useChip(caster, template, target, targets, cellEntity)
        if critical:
            self.statistics.critical(caster)

        if template.getCooldown() != 0:
            self.addCooldown(caster, template)

        caster.useTP(template.getCost())
        caster.addItemUse(template.getId())

        return result

    def moveEntity(self, entity, path_or_cell) -> int:
        from ..attack.entity_state import EntityState
        from ..maps.cell import Cell
        from ..action.action_move import ActionMove

        # path_or_cell can be either a List<Cell> or a single Cell
        if isinstance(path_or_cell, Cell):
            cell = path_or_cell
            if entity.hasState(EntityState.STATIC):
                return 0
            self.map.moveEntity(entity, cell)
            return 0

        path = path_or_cell
        if entity.hasState(EntityState.STATIC):
            return 0

        size = len(path)
        if size == 0:
            return 0
        if size > entity.getMP():
            return 0

        self.actions.log(ActionMove(entity, path))
        self.statistics.move(entity, entity, entity.getCell(), path)

        entity.useMP(size)
        self.map.moveEntity(entity, path[len(path) - 1])

        return len(path)

    def teleportEntity(self, entity, cell, caster, itemId: int) -> None:
        start = entity.getCell()
        self.map.moveEntity(entity, cell)
        self.statistics.move(caster, entity, start, [cell])
        if start is not cell:
            entity.onMoved(caster)
        self.statistics.teleportation(entity, caster, start, cell, itemId)

    def slideEntity(self, entity, cell, caster) -> None:
        from ..attack.entity_state import EntityState

        if entity.hasState(EntityState.STATIC):
            return

        start = entity.getCell()

        if cell is not start:
            self.map.moveEntity(entity, cell)
            self.statistics.move(caster, entity, start, self.map.getAStarPath(start, [cell], [cell, start]))
            self.statistics.slide(entity, caster, start, cell)
            entity.onMoved(caster)

    def invertEntities(self, caster, target) -> None:
        from ..attack.entity_state import EntityState

        if target.hasState(EntityState.STATIC):
            return

        start = caster.getCell()
        end = target.getCell()
        if start is None or end is None:
            return

        self.map.invertEntities(caster, target)

        self.statistics.move(caster, caster, start, [end])
        self.statistics.move(caster, target, end, [start])

        target.onMoved(caster)
        caster.onMoved(caster)

    def summonEntity(self, caster, target, template, name=None) -> int:
        from ..effect.effect import Effect

        params = template.getAttack().getEffectParametersByType(Effect.TYPE_SUMMON)
        if self.order.current() is not caster or params is None:
            return -1
        if template.getCost() > caster.getTP():
            return -2
        if self.hasCooldown(caster, template):
            return -3
        if not self.map.canUseAttack(caster.getCell(), target, template.getAttack()):
            return -4
        if not target.available(self.map):
            return -4
        if self.teams[caster.getTeam()].getSummonCount() >= State.SUMMON_LIMIT:
            return -5

        critical = self.generateCritical(caster)
        result = Attack.USE_CRITICAL if critical else Attack.USE_SUCCESS

        log = ActionUseChip(target, template, result)
        self.actions.log(log)
        if critical:
            caster.onCritical()

        summon = self.createSummon(caster, int(params.getValue1()), target, template.getLevel(), critical, name)

        self.actions.log(ActionInvocation(summon, result))
        self.statistics.summon(caster, summon)
        self.statistics.useChip(caster, template, target, [], None)

        if template.getCooldown() != 0:
            self.addCooldown(caster, template)

        caster.useTP(template.getCost())

        return result

    def resurrectEntity(self, caster, target, template, target_entity, fullLife) -> int:
        from ..effect.effect import Effect

        if self.order.current() is not caster:
            return Attack.USE_INVALID_TARGET
        if template.getCost() > caster.getTP():
            return Attack.USE_NOT_ENOUGH_TP
        if not self.map.canUseAttack(caster.getCell(), target, template.getAttack()):
            return Attack.USE_INVALID_POSITION
        if self.hasCooldown(caster, template):
            return Attack.USE_INVALID_COOLDOWN
        params = template.getAttack().getEffectParametersByType(Effect.TYPE_RESURRECT)
        if params is None or not target.available(self.map) or not target_entity.isDead():
            return Attack.USE_INVALID_TARGET

        if target_entity.isSummon():
            if self.teams[target_entity.getTeam()].getSummonCount() >= State.SUMMON_LIMIT:
                return Attack.USE_TOO_MANY_SUMMONS

        critical = self.generateCritical(caster)
        result = Attack.USE_CRITICAL if critical else Attack.USE_SUCCESS

        log = ActionUseChip(target, template, result)
        self.actions.log(log)
        if critical:
            caster.onCritical()

        self.resurrect(caster, target_entity, target, critical, fullLife)
        self.statistics.useChip(caster, template, target, [], None)
        self.statistics.resurrect(caster, target_entity)

        if template.getCooldown() != 0:
            self.addCooldown(caster, template)

        # Hardcode awekening invulnerability
        if result > 0 and template.getId() == 415:
            Effect.createEffect(self, Effect.TYPE_ADD_STATE, -1, 1.0, 3.0, 3.0, critical, target_entity, caster, template.getAttack(), 1.0, True, 0, 1, 0, Effect.MODIFIER_IRREDUCTIBLE)

        caster.useTP(template.getCost())

        return result

    def generateCritical(self, caster) -> bool:
        return self.getRandom().get_double() < (caster.getAgility() / 1000.0)

    def createSummon(self, owner, type_, target, level, critical, name=None):
        from ..entity.bulb import Bulb

        fid = self.getNextEntityId()
        invoc = Bulb.create(owner, -fid, type_, level, critical, name)
        invoc.setState(self, fid)

        team = owner.getTeam()
        invoc.setTeam(team)
        self.teams[team].addEntity(invoc)

        self.mEntities[invoc.getFId()] = invoc
        self.order.addSummon(owner, invoc)
        self.map.setEntity(invoc, target)
        self.actions.addEntity(invoc, critical)

        return invoc

    def removeInvocation(self, invoc, force: bool) -> None:
        self.teams[invoc.getTeam()].removeEntity(invoc)
        if force:
            del self.mEntities[invoc.getFId()]

    def resurrect(self, owner, entity, cell, critical, fullLife) -> None:
        from ..effect.effect import Effect
        from ..action.action_resurrect import ActionResurrect
        next_ = None
        start = False
        for e in self.initialOrder:
            if e is entity:
                start = True
                continue
            if not start:
                continue
            if e.isDead():
                continue
            next_ = e
            break
        if next_ is None:
            self.order.addEntity(entity)
        else:
            self.order.addEntity(self.order.getEntityTurnOrder(next_) - 1, entity)
        entity.resurrect(owner, Effect.CRITICAL_FACTOR if critical else 1.0, fullLife)
        self.map.setEntity(entity, cell)
        self.actions.log(ActionResurrect(owner, entity))

    def getTurn(self) -> int:
        return self.order.getTurn()

    def getOrder(self):
        return self.order

    def getActions(self):
        return self.actions

    def getFullType(self) -> int:
        return self.fullType

    def setId(self, f: int) -> None:
        self.mId = f

    def getLeeks(self):
        retour = {}
        for k, v in self.mEntities.items():
            l = v.getLeek()
            if l is not None:
                retour[k] = l
        return retour

    def getNextEntityId(self) -> int:
        id_ = self.mNextEntityId
        self.mNextEntityId += 1
        return id_

    def addCooldown(self, entity, chip, cooldown=None) -> None:
        if chip is None:
            return
        if cooldown is None:
            cooldown = chip.getCooldown()
        if chip.isTeamCooldown():
            self.teams[entity.getTeam()].addCooldown(chip, cooldown)
        else:
            entity.addCooldown(chip, cooldown)

    def hasCooldown(self, entity, chip) -> bool:
        if chip is None:
            return False
        if chip.isTeamCooldown():
            return self.teams[entity.getTeam()].hasCooldown(chip.getId())
        else:
            return entity.hasCooldown(chip.getId())

    def getCooldown(self, entity, chip) -> int:
        if chip is None:
            return 0
        if chip.isTeamCooldown():
            return self.teams[entity.getTeam()].getCooldown(chip.getId())
        else:
            return entity.getCooldown(chip.getId())

    def getType(self) -> int:
        return self.type

    def getContext(self) -> int:
        return self.context

    @staticmethod
    def getFightContext(type_: int) -> int:
        if type_ in (State.TYPE_SOLO_GARDEN, State.TYPE_TEAM_GARDEN, State.TYPE_FARMER_GARDEN, State.FULL_TYPE_WAR_GARDEN, State.FULL_TYPE_CHEST_HUNT_GARDEN, State.FULL_TYPE_COLOSSUS_GARDEN):
            return State.CONTEXT_GARDEN
        elif type_ in (State.TYPE_SOLO_TEST, State.TYPE_TEAM_TEST, State.TYPE_FARMER_TEST):
            return State.CONTEXT_TEST
        elif type_ in (State.TYPE_TEAM_TOURNAMENT, State.TYPE_SOLO_TOURNAMENT, State.TYPE_FARMER_TOURNAMENT, State.FULL_TYPE_WAR_AUTO, State.FULL_TYPE_CHEST_HUNT_AUTO, State.FULL_TYPE_COLOSSUS_AUTO):
            return State.CONTEXT_TOURNAMENT
        elif type_ == State.FULL_TYPE_BATTLE_ROYALE:
            return State.CONTEXT_BATTLE_ROYALE
        return State.CONTEXT_CHALLENGE

    @staticmethod
    def getFightType(type_: int) -> int:
        if type_ in (State.TYPE_SOLO_GARDEN, State.TYPE_SOLO_CHALLENGE, State.TYPE_SOLO_TOURNAMENT, State.TYPE_SOLO_TEST):
            return State.TYPE_SOLO
        elif type_ in (State.TYPE_FARMER_GARDEN, State.TYPE_FARMER_TOURNAMENT, State.TYPE_FARMER_CHALLENGE, State.TYPE_FARMER_TEST):
            return State.TYPE_FARMER
        elif type_ == State.FULL_TYPE_BATTLE_ROYALE:
            return State.TYPE_BATTLE_ROYALE
        elif type_ in (State.FULL_TYPE_WAR_GARDEN, State.FULL_TYPE_WAR_AUTO):
            return State.TYPE_WAR
        elif type_ in (State.FULL_TYPE_CHEST_HUNT_GARDEN, State.FULL_TYPE_CHEST_HUNT_AUTO):
            return State.TYPE_CHEST_HUNT
        elif type_ in (State.FULL_TYPE_COLOSSUS_GARDEN, State.FULL_TYPE_COLOSSUS_AUTO):
            return State.TYPE_COLOSSUS
        return State.TYPE_TEAM

    @staticmethod
    def isTeamAIFight(type_: int) -> bool:
        return State.getFightType(type_) != State.TYPE_SOLO

    @staticmethod
    def isTestFight(type_: int) -> bool:
        return State.getFightContext(type_) == State.CONTEXT_TEST

    @staticmethod
    def isChallenge(type_: int) -> bool:
        return State.getFightContext(type_) == State.CONTEXT_CHALLENGE

    def getTeams(self):
        return self.teams

    def getDeadReport(self):
        dead = {}
        for team in self.teams:
            for entity in team.getEntities():
                dead[str(entity.getId())] = entity.isDead()
        return dead

    def setContext(self, context: int) -> None:
        self.context = context

    def setType(self, type_: int) -> None:
        self.type = type_

    def _getFactionProgress(self) -> float:
        teamCount = len(self.teams)
        if teamCount <= 1:
            return 0
        progress = 0
        for team in self.teams:
            progress += team.getLifeRatio()
        return 1 - progress / teamCount

    def getProgress(self) -> float:
        if self.order is None:
            return 0
        entityCount = len(self.order.getEntities())
        f = self._getFactionProgress()
        t = min(1, math.pow((self.getTurn() * entityCount + self.order.getPosition()) / (State.MAX_TURNS * entityCount), 0.5))
        return max(t, f)

    def seed(self, seed: int) -> None:
        self.seed_val = seed
        self.randomGenerator.seed(seed)

    def getRandom(self):
        return self.randomGenerator

    def setRegisterManager(self, registerManager) -> None:
        self.registerManager = registerManager

    def getRegisterManager(self):
        return self.registerManager

    def getDate(self):
        return self.date

    def setStatisticsManager(self, statisticsManager) -> None:
        self.statistics = statisticsManager

    def getDuration(self) -> int:
        return self.order.getTurn()

    def getLastEntity(self):
        return self.mEntities.get(self.mNextEntityId - 1)

    def getState(self) -> int:
        return self.mState

    def setState(self, state: int) -> None:
        self.mState = state

    def getSeed(self) -> int:
        return self.seed_val

    def __str__(self) -> str:
        from ..items import items as Items
        from ..chips import chips as Chips
        from ..weapons import weapons as Weapons

        lines = []
        for entity in self.mEntities.values():
            prefix = "[*] " if self.order is not None and self.order.current() is entity else ""
            s = (prefix + entity.getName()
                 + " life=" + str(entity.getLife()) + "/" + str(entity.getTotalLife())
                 + " str=" + str(entity.getStrength())
                 + " agi=" + str(entity.getAgility())
                 + " res=" + str(entity.getResistance())
                 + " tp=" + str(entity.getTP())
                 + " mp=" + str(entity.getMP())
                 + " rel_sh=" + str(entity.getRelativeShield()) + "%"
                 + " abs_sh=" + str(entity.getAbsoluteShield())
                 + " pos=" + str(entity.getCell()))
            for chip_id, value in entity.getCooldowns().items():
                if value > 0:
                    item_type = Items.getType(chip_id)
                    if item_type == Items.TYPE_CHIP:
                        name = Chips.getChip(chip_id).getName()
                    else:
                        name = Weapons.getWeapon(chip_id).getName()
                    s += " " + name[:4] + "=" + str(value)
            lines.append(s)
        return "State [\n\t" + "\n\t".join(lines) + "\n]"

    def moveToward(self, entity_or_id, leek_id: int, pm_to_use: int) -> int:
        if not isinstance(entity_or_id, Entity):
            entity = self.getEntity(entity_or_id)
        else:
            entity = entity_or_id

        pm = entity.getMP() if pm_to_use == -1 else int(pm_to_use)
        if pm > entity.getMP():
            pm = entity.getMP()
        used_pm = 0
        if pm > 0:
            target = self.getEntity(leek_id)
            if target is not None and not target.isDead():
                path = self.getMap().getPathBeetween(entity.getCell(), target.getCell(), None)
                if path is not None:
                    used_pm = self.moveEntity(entity, path[:min(len(path), pm)])
        return used_pm

    def moveTowardCell(self, entity_or_id, cell_id: int, pm_to_use: int) -> int:
        if not isinstance(entity_or_id, Entity):
            entity = self.getEntity(entity_or_id)
        else:
            entity = entity_or_id

        pm = entity.getMP() if pm_to_use == -1 else int(pm_to_use)
        if pm > entity.getMP():
            pm = entity.getMP()
        used_pm = 0
        if pm > 0 and entity.getCell() is not None:
            target = self.map.getCell(int(cell_id))
            if target is not None and target is not entity.getCell():
                path = None
                if not target.isWalkable():
                    path = self.map.getAStarPath(entity.getCell(), self.map.getValidCellsAroundObstacle(target), None)
                else:
                    path = self.getMap().getPathBeetween(entity.getCell(), target, None)
                if path is not None:
                    used_pm = self.moveEntity(entity, path[:min(pm, len(path))])
        return used_pm
