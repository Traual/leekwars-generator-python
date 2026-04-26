import math

from .stats import Stats
from ..util.java_math import java_round


class Entity:

    SAY_LIMIT_TURN = 2
    SHOW_LIMIT_TURN = 5

    TYPE_LEEK = 0
    TYPE_BULB = 1
    TYPE_TURRET = 2
    TYPE_CHEST = 3
    TYPE_MOB = 4

    # Stats constants
    STAT_LIFE = 0
    STAT_TP = 1
    STAT_MP = 2
    STAT_STRENGTH = 3
    STAT_AGILITY = 4
    STAT_FREQUENCY = 5
    STAT_WISDOM = 6
    STAT_ABSOLUTE_SHIELD = 9
    STAT_RELATIVE_SHIELD = 10
    STAT_RESISTANCE = 11
    STAT_SCIENCE = 12
    STAT_MAGIC = 13
    STAT_DAMAGE_RETURN = 14
    STAT_POWER = 15
    STAT_CORES = 16
    STAT_RAM = 17

    def __init__(self, *args):
        # Several constructor variants:
        # () -> calls (0, "")
        # (id, name) -> simple
        # (id, name, farmer, level, life, ...) -> full
        # (Entity) -> copy

        # Init common state
        self.cell = None
        self.name = ""
        self.mId = 0
        self.fight_id = 0
        self.mFarmer = 0
        self.mLevel = 1
        self.mSkin = 0
        self.mHat = -1
        self.mMetal = False
        self.mFace = 0
        self.mFarmerName = ""
        self.mFarmerCountry = None
        self.mTeamName = ""
        self.mCompositionName = None
        self.mAIName = ""
        self.mTeamId = 0
        self.mAIId = 0
        self.mTotalLife = 0
        self.mInitialLife = 0
        self.mStatic = False
        self.resurrected = 0
        self.totalOperations = 0
        self.saysTurn = 0
        self.showsTurn = 0
        self.mBirthTurn = 1

        self.effects = []
        self.launchedEffects = []
        self.passiveEffects = []
        self.mCooldown = {}
        self.states = set()
        self.team = 0
        self.state = None
        self.mChips = {}
        self.mWeapons = []
        self.weapon = None
        self.itemUses = {}
        self.usedTP = 0
        self.usedMP = 0
        self.life = 0
        self.mRegister = None
        self.mHasMoved = False
        self.ai = None
        self.logs = None
        self.fight = None
        self.aiFile = None
        self.initialCell = None
        self.orientation = -1

        if len(args) == 0:
            self._init_simple(0, "")
        elif len(args) == 1 and isinstance(args[0], Entity):
            self._init_copy(args[0])
        elif len(args) == 2:
            self._init_simple(args[0], args[1])
        else:
            self._init_full(*args)

        self.mBaseStats = self.mBaseStats if hasattr(self, 'mBaseStats') else Stats()
        self.mBuffStats = self.mBuffStats if hasattr(self, 'mBuffStats') else Stats()

    def _init_simple(self, id_, name):
        self.mId = id_ if id_ is not None else 0
        self.name = name
        self.mLevel = 1
        self.mFarmer = 0
        self.mSkin = 0
        self.mHat = -1

        self.mBuffStats = Stats()
        self.mBaseStats = Stats()
        self.mBaseStats.setStat(Entity.STAT_LIFE, 0)
        self.mBaseStats.setStat(Entity.STAT_TP, 0)
        self.mBaseStats.setStat(Entity.STAT_MP, 0)
        self.mBaseStats.setStat(Entity.STAT_STRENGTH, 0)
        self.mBaseStats.setStat(Entity.STAT_AGILITY, 0)
        self.mBaseStats.setStat(Entity.STAT_FREQUENCY, 0)
        self.mBaseStats.setStat(Entity.STAT_WISDOM, 0)
        self.mBaseStats.setStat(Entity.STAT_RESISTANCE, 0)
        self.mBaseStats.setStat(Entity.STAT_SCIENCE, 0)
        self.mBaseStats.setStat(Entity.STAT_MAGIC, 0)
        self.mBaseStats.setStat(Entity.STAT_CORES, 0)
        self.mBaseStats.setStat(Entity.STAT_RAM, 0)

        self.mTotalLife = self.mBaseStats.getStat(Entity.STAT_LIFE)
        self.life = self.mTotalLife

        self.mWeapons = []
        self.endTurn()

    def _init_full(self, id_, name, farmer, level, life, turn_point, move_point, force, agility, frequency, wisdom, resistance, science, magic, cores, ram, skin, metal, face, team_id, team_name, ai_id, ai_name, farmer_name, farmer_country, hat):
        self.mId = id_ if id_ is not None else 0
        self.name = name
        self.mLevel = level
        self.mFarmer = farmer
        self.mSkin = skin
        self.mHat = hat
        self.mMetal = metal
        self.mFace = face

        self.mBuffStats = Stats()
        self.mBaseStats = Stats()
        self.mBaseStats.setStat(Entity.STAT_LIFE, life)
        self.mBaseStats.setStat(Entity.STAT_TP, turn_point)
        self.mBaseStats.setStat(Entity.STAT_MP, move_point)
        self.mBaseStats.setStat(Entity.STAT_STRENGTH, force)
        self.mBaseStats.setStat(Entity.STAT_AGILITY, agility)
        self.mBaseStats.setStat(Entity.STAT_FREQUENCY, frequency)
        self.mBaseStats.setStat(Entity.STAT_WISDOM, wisdom)
        self.mBaseStats.setStat(Entity.STAT_RESISTANCE, resistance)
        self.mBaseStats.setStat(Entity.STAT_SCIENCE, science)
        self.mBaseStats.setStat(Entity.STAT_MAGIC, magic)
        self.mBaseStats.setStat(Entity.STAT_CORES, cores)
        self.mBaseStats.setStat(Entity.STAT_RAM, ram)

        self.mTotalLife = self.mBaseStats.getStat(Entity.STAT_LIFE)
        self.mInitialLife = self.mTotalLife
        self.life = self.mTotalLife

        self.mWeapons = []
        self.mTeamName = team_name
        self.mTeamId = team_id
        self.mFarmerName = farmer_name
        self.mFarmerCountry = farmer_country
        self.mAIName = ai_name
        self.mAIId = ai_id

        self.endTurn()

    def _init_copy(self, entity):
        self.mId = entity.getId()
        self.fight_id = entity.fight_id
        self.name = entity.getName()
        self.team = entity.getTeam()
        self.mLevel = entity.mLevel
        self.mFarmer = entity.getFarmer()
        self.mBuffStats = Stats(entity.mBuffStats)
        self.mBaseStats = Stats(entity.mBaseStats)
        self.mInitialLife = entity.mInitialLife
        self.mTotalLife = entity.mTotalLife
        self.mStatic = entity.mStatic
        self.saysTurn = entity.saysTurn
        self.showsTurn = entity.showsTurn
        self.resurrected = entity.resurrected
        self.cell = entity.cell
        self.life = entity.getLife()
        self.mWeapons = entity.mWeapons  # immutable
        self.mChips = entity.mChips  # immutable
        self.weapon = entity.weapon
        self.mCooldown = dict(entity.mCooldown)
        self.usedTP = entity.usedTP
        self.usedMP = entity.usedMP
        self.passiveEffects = entity.passiveEffects  # immutable

    def getLeek(self):
        return None

    def getType(self) -> int:
        raise NotImplementedError

    def setCell(self, cell) -> None:
        self.cell = cell

    def setRegisters(self, registre) -> None:
        self.mRegister = registre

    def getRegisters(self):
        return self.mRegister

    def _loadRegisters(self) -> None:
        from ..leek.registers import Registers
        v = self.state.getRegisterManager().getRegisters(self.getId())
        if v is None:
            self.mRegister = Registers(True)
        else:
            self.mRegister = Registers.fromJSONString(v)

    def getRegister(self, key: str):
        if self.mRegister is None:
            self._loadRegisters()
        return self.mRegister.get(key)

    def getAllRegisters(self):
        if self.mRegister is None:
            self._loadRegisters()
        return self.mRegister.getValues()

    def setRegister(self, key: str, value: str) -> bool:
        if self.mRegister is None:
            self._loadRegisters()
        self.state.statistics.registerWrite(self, key, value)
        return self.mRegister.set(key, value)

    def deleteRegister(self, key: str) -> None:
        if self.mRegister is not None:
            self.mRegister.delete(key)

    def getHat(self) -> int:
        return self.mHat

    def getTeamId(self) -> int:
        return self.mTeamId

    def getTeamName(self) -> str:
        return self.mTeamName

    def getCompositionName(self):
        return self.mCompositionName

    def getAIName(self) -> str:
        return self.mAIName

    def getAIId(self) -> int:
        return self.mAIId

    def getFarmerName(self) -> str:
        return self.mFarmerName

    def getFarmerCountry(self) -> str:
        if self.mFarmerCountry is None:
            return "?"
        return self.mFarmerCountry

    def addWeapon(self, w) -> None:
        self.mWeapons.append(w)
        self.passiveEffects.extend(w.getPassiveEffects())

    def getBaseStats(self) -> Stats:
        return self.mBaseStats

    def getCell(self):
        return self.cell

    def getFId(self) -> int:
        return self.fight_id

    def getId(self) -> int:
        return self.mId

    def setId(self, id_: int) -> None:
        self.mId = id_

    def getLevel(self) -> int:
        return self.mLevel

    def getLife(self) -> int:
        return self.life

    def getTotalLife(self) -> int:
        return self.mTotalLife

    def addTotalLife(self, vitality: int, caster) -> None:
        self.mTotalLife += vitality
        self.state.statistics.vitality(self, caster, vitality)

    def setTotalLife(self, vitality: int) -> None:
        self.mTotalLife = vitality
        self.mInitialLife = vitality

    def getInitialLife(self) -> int:
        return self.mInitialLife

    def setName(self, name: str) -> None:
        self.name = name

    def getName(self) -> str:
        return self.name

    def getStat(self, id_: int) -> int:
        return self.mBaseStats.getStat(id_) + self.mBuffStats.getStat(id_)

    def getStrength(self) -> int:
        return self.getStat(Entity.STAT_STRENGTH)

    def getAgility(self) -> int:
        return self.getStat(Entity.STAT_AGILITY)

    def getResistance(self) -> int:
        return self.getStat(Entity.STAT_RESISTANCE)

    def getScience(self) -> int:
        return self.getStat(Entity.STAT_SCIENCE)

    def getMagic(self) -> int:
        return self.getStat(Entity.STAT_MAGIC)

    def getWisdom(self) -> int:
        return self.getStat(Entity.STAT_WISDOM)

    def getRelativeShield(self) -> int:
        return self.getStat(Entity.STAT_RELATIVE_SHIELD)

    def getAbsoluteShield(self) -> int:
        return self.getStat(Entity.STAT_ABSOLUTE_SHIELD)

    def getDamageReturn(self) -> int:
        return self.getStat(Entity.STAT_DAMAGE_RETURN)

    def getFrequency(self) -> int:
        return self.getStat(Entity.STAT_FREQUENCY)

    def getCores(self) -> int:
        return self.getStat(Entity.STAT_CORES)

    def getRAM(self) -> int:
        return self.getStat(Entity.STAT_RAM)

    def getTotalTP(self) -> int:
        return self.getStat(Entity.STAT_TP)

    def getTotalMP(self) -> int:
        return self.getStat(Entity.STAT_MP)

    def getMP(self) -> int:
        return self.getTotalMP() - self.usedMP

    def getTP(self) -> int:
        return self.getTotalTP() - self.usedTP

    def getPower(self) -> int:
        return self.getStat(Entity.STAT_POWER)

    def getTeam(self) -> int:
        return self.team

    def getWeapon(self):
        return self.weapon

    def hasWeapon(self, id_tmp: int) -> bool:
        for w in self.mWeapons:
            if w.getId() == id_tmp:
                return True
        return False

    def getWeapons(self):
        return self.mWeapons

    def isDead(self) -> bool:
        return self.life <= 0

    def removeLife(self, pv: int, erosion: int, attacker, type_, effect, item) -> None:
        from ..attack.damage_type import DamageType
        if self.isDead():
            return
        if pv > self.life:
            pv = self.life
        self.life -= pv

        # Add erosion
        self.mTotalLife -= erosion
        if self.mTotalLife < 1:
            self.mTotalLife = 1

        if pv > 0:
            self.state.statistics.damage(self, attacker, pv, type_, effect)
        if erosion > 0:
            self.state.statistics.damage(self, attacker, erosion, DamageType.NOVA, effect)

        if self.life <= 0:
            self.state.onPlayerDie(self, attacker, item)
            self.die()

    def onDirectDamage(self, damage: int) -> None:
        if self.isDead():
            return
        for weapon in self.mWeapons:
            for effect in weapon.getPassiveEffects():
                self.activateOnDamagePassiveEffect(effect, weapon.getAttack(), damage)

    def onNovaDamage(self, damage: int) -> None:
        if self.isDead():
            return
        for weapon in self.mWeapons:
            for effect in weapon.getPassiveEffects():
                self.activateOnNovaDamagePassiveEffect(effect, weapon.getAttack(), damage)

    def onPoisonDamage(self, damage: int) -> None:
        if self.isDead():
            return
        for weapon in self.mWeapons:
            for effect in weapon.getPassiveEffects():
                self.activateOnPoisonDamagePassiveEffect(effect, weapon.getAttack(), damage)

    def onMoved(self, by) -> None:
        if self.isDead():
            return
        if by is self:
            return  # Déplacement subi uniquement
        for weapon in self.mWeapons:
            for effect in weapon.getPassiveEffects():
                self.activateOnMovedPassiveEffect(effect, weapon.getAttack())

    def onAllyKilled(self) -> None:
        if self.isDead():
            return
        for weapon in self.mWeapons:
            for effect in weapon.getPassiveEffects():
                self.activateOnAllyKilledPassiveEffect(effect, weapon.getAttack())

    def onCritical(self) -> None:
        if self.isDead():
            return
        for weapon in self.mWeapons:
            for effect in weapon.getPassiveEffects():
                self.activateOnCriticalPassiveEffect(effect, weapon.getAttack())

    def onKill(self) -> None:
        if self.isDead():
            return
        for weapon in self.mWeapons:
            for effect in weapon.getPassiveEffects():
                self.activateOnKillPassiveEffect(effect, weapon.getAttack())

    def activateOnMovedPassiveEffect(self, effect, attack) -> None:
        from ..effect.effect import Effect
        if effect.getId() == Effect.TYPE_MOVED_TO_MP:
            value = effect.getValue1()
            stackable = (effect.getModifiers() & Effect.MODIFIER_STACKABLE) != 0
            Effect.createEffect(self.state, Effect.TYPE_RAW_BUFF_MP, effect.getTurns(), 1, value, 0, False,
                                self, self, attack, 0, stackable, 0, 1, 0, effect.getModifiers())

    def activateOnDamagePassiveEffect(self, effect, attack, inputValue: int) -> None:
        from ..effect.effect import Effect
        if effect.getId() == Effect.TYPE_DAMAGE_TO_ABSOLUTE_SHIELD:
            value = inputValue * (effect.getValue1() / 100.0)
            stackable = (effect.getModifiers() & Effect.MODIFIER_STACKABLE) != 0
            Effect.createEffect(self.state, Effect.TYPE_RAW_ABSOLUTE_SHIELD, effect.getTurns(), 1, value, 0, False,
                                self, self, attack, 0, stackable, 0, 0, 0, effect.getModifiers())
        elif effect.getId() == Effect.TYPE_DAMAGE_TO_STRENGTH:
            value = inputValue * (effect.getValue1() / 100.0)
            stackable = (effect.getModifiers() & Effect.MODIFIER_STACKABLE) != 0
            Effect.createEffect(self.state, Effect.TYPE_RAW_BUFF_STRENGTH, effect.getTurns(), 1, value, 0, False,
                                self, self, attack, 0, stackable, 0, 0, 0, effect.getModifiers())

    def activateOnNovaDamagePassiveEffect(self, effect, attack, inputValue: int) -> None:
        from ..effect.effect import Effect
        if effect.getId() == Effect.TYPE_NOVA_DAMAGE_TO_MAGIC:
            value = inputValue * (effect.getValue1() / 100.0)
            stackable = (effect.getModifiers() & Effect.MODIFIER_STACKABLE) != 0
            Effect.createEffect(self.state, Effect.TYPE_RAW_BUFF_MAGIC, effect.getTurns(), 1, value, 0, False,
                                self, self, attack, 0, stackable, 0, 0, 0, effect.getModifiers())

    def activateOnPoisonDamagePassiveEffect(self, effect, attack, inputValue: int) -> None:
        from ..effect.effect import Effect
        if effect.getId() == Effect.TYPE_POISON_TO_SCIENCE:
            value = inputValue * (effect.getValue1() / 100.0)
            stackable = (effect.getModifiers() & Effect.MODIFIER_STACKABLE) != 0
            Effect.createEffect(self.state, Effect.TYPE_RAW_BUFF_SCIENCE, effect.getTurns(), 1, value, 0, False,
                                self, self, attack, 0, stackable, 0, 0, 0, effect.getModifiers())

    def activateOnAllyKilledPassiveEffect(self, effect, attack) -> None:
        from ..effect.effect import Effect
        if effect.getId() == Effect.TYPE_ALLY_KILLED_TO_AGILITY:
            value = effect.getValue1()
            stackable = (effect.getModifiers() & Effect.MODIFIER_STACKABLE) != 0
            Effect.createEffect(self.state, Effect.TYPE_RAW_BUFF_AGILITY, effect.getTurns(), 1, value, 0, False,
                                self, self, attack, 0, stackable, 0, 0, 0, effect.getModifiers())

    def activateOnCriticalPassiveEffect(self, effect, attack) -> None:
        from ..effect.effect import Effect
        if effect.getId() == Effect.TYPE_CRITICAL_TO_HEAL:
            if self.getLife() < self.getTotalLife():
                value1 = effect.getValue1()
                value2 = effect.getValue2()
                jet = self.state.getRandom().get_double()
                Effect.createEffect(self.state, Effect.TYPE_RAW_HEAL, 0, 1, value1, value2, False,
                                    self, self, attack, jet, False, 0, 1, 0, effect.getModifiers())

    def activateOnKillPassiveEffect(self, effect, attack) -> None:
        from ..effect.effect import Effect
        if effect.getId() == Effect.TYPE_KILL_TO_TP:
            value = effect.getValue1()
            Effect.createEffect(self.state, Effect.TYPE_RAW_BUFF_TP, effect.getTurns(), 1, value, value, False,
                                self, self, attack, 0, True, 0, 1, 0, effect.getModifiers())

    def addLife(self, healer, pv: int) -> None:
        if pv > self.getTotalLife() - self.life:
            pv = self.getTotalLife() - self.life
        self.life += pv
        self.state.statistics.heal(healer, self, pv)
        self.state.statistics.characteristics(self)

    def setTeam(self, team: int) -> None:
        self.team = team

    def setWeapon(self, weapon) -> None:
        self.weapon = weapon

    def startTurn(self) -> None:
        self.applyCoolDown()
        self.state.statistics.entityTurn(self)
        effectsCopy = list(self.effects)
        for effect in effectsCopy:
            effect.applyStartTurn(self.state)
            if self.isDead():
                return

        e = 0
        while e < len(self.launchedEffects):
            effect = self.launchedEffects[e]
            if effect.getTurns() != -1:
                effect.setTurns(effect.getTurns() - 1)
            if effect.getTurns() == 0:
                effect.getTarget().removeEffect(effect)
                self.launchedEffects.pop(e)
                e -= 1
            e += 1

    def endTurn(self) -> None:
        from ..effect.effect import Effect

        self.usedMP = 0
        self.usedTP = 0
        self.saysTurn = 0
        self.showsTurn = 0

        self.itemUses.clear()

        # Propagation des effets
        for effect in self.effects:
            if effect.propagate > 0:
                attack = effect.getAttack()
                propagation = attack.getEffects()[0]
                original = attack.getEffects()[1]
                jet = self.state.getRandom().get_double()
                for target in self.getEntitiesAround(effect.propagate):
                    if (propagation.getModifiers() & Effect.MODIFIER_NOT_REPLACEABLE) != 0 and target.hasEffect(attack.getItemId()):
                        continue
                    Effect.createEffect(self.state, effect.getID(), original.getTurns(), 1,
                                        original.getValue1(), original.getValue2(), effect.isCritical(),
                                        target, effect.getCaster(), attack, jet,
                                        (propagation.getModifiers() & Effect.MODIFIER_STACKABLE) != 0,
                                        0, 0, effect.propagate, effect.modifiers)

    def hasEffect(self, attackID: int) -> bool:
        for target_effect in self.effects:
            if target_effect.getAttack() is not None and target_effect.getAttack().getItemId() == attackID:
                return True
        return False

    def die(self) -> None:
        self.life = 0
        # Remove launched effects
        while len(self.launchedEffects) > 0:
            effect = self.launchedEffects[0]
            effect.getTarget().removeEffect(effect)
            self.launchedEffects.pop(0)
        # Remove effects
        while len(self.effects) > 0:
            effect = self.effects[0]
            effect.getCaster().removeLaunchedEffect(effect)
            self.effects.pop(0)
        self.updateBuffStats()
        # Kill summons
        entities = list(self.state.getTeamEntities(self.getTeam()))
        for e in entities:
            if e.isSummon() and e.getSummoner().getFId() == self.getFId():
                self.state.onPlayerDie(e, None, None)
                e.die()

    def updateBuffStats(self, *args) -> None:
        if len(args) == 0:
            self.mBuffStats.clear()
            self.states.clear()
            for effect in self.effects:
                if effect.getStats() is not None:
                    self.mBuffStats.addStats(effect.getStats())
                if effect.getState() is not None:
                    self.states.add(effect.getState())
        else:
            id_, delta, caster = args
            self.mBuffStats.updateStat(id_, delta)
            self.state.statistics.characteristics(self)
            self.state.statistics.updateStat(self, id_, delta, caster)

    def addEffect(self, effect) -> None:
        self.effects.append(effect)

    def removeEffect(self, effect) -> None:
        from ..action.action_remove_effect import ActionRemoveEffect
        self.state.log(ActionRemoveEffect(effect.getLogID()))
        if effect in self.effects:
            self.effects.remove(effect)
        self.updateBuffStats()

    def addLaunchedEffect(self, effect) -> None:
        self.launchedEffects.append(effect)

    def removeLaunchedEffect(self, effect) -> None:
        if effect in self.launchedEffects:
            self.launchedEffects.remove(effect)

    def updateEffect(self, effect) -> None:
        from ..action.action_update_effect import ActionUpdateEffect
        self.state.log(ActionUpdateEffect(effect.getLogID(), effect.value))

    def clearEffects(self) -> None:
        i = 0
        while i < len(self.effects):
            effect = self.effects[i]
            effect.getCaster().removeLaunchedEffect(effect)
            self.removeEffect(effect)
            i -= 1
            i += 1
        self.effects.clear()

    def reduceEffects(self, percent: float, caster) -> None:
        from ..effect.effect import Effect
        i = 0
        while i < len(self.effects):
            effect = self.effects[i]
            if (effect.getModifiers() & Effect.MODIFIER_IRREDUCTIBLE) != 0:
                i += 1
                continue
            effect.reduce(percent, caster)
            if effect.value <= 0:
                effect.getCaster().removeLaunchedEffect(effect)
                self.removeEffect(self.effects[i])
                i -= 1
            else:
                self.updateEffect(self.effects[i])
            i += 1
        self.updateBuffStats()

    def reduceEffectsTotal(self, percent: float, caster) -> None:
        i = 0
        while i < len(self.effects):
            effect = self.effects[i]
            effect.reduce(percent, caster)
            if effect.value <= 0:
                effect.getCaster().removeLaunchedEffect(effect)
                self.removeEffect(effect)
                i -= 1
            else:
                self.updateEffect(effect)
            i += 1
        self.updateBuffStats()

    def clearPoisons(self, caster) -> None:
        from ..effect.effect_poison import EffectPoison
        poisonsRemoved = 0
        i = 0
        while i < len(self.effects):
            effect = self.effects[i]
            if isinstance(effect, EffectPoison):
                effect.getCaster().removeLaunchedEffect(effect)
                self.removeEffect(effect)
                i -= 1
                poisonsRemoved += effect.getValue()
            i += 1
        self.state.statistics.antidote(self, caster, poisonsRemoved)

    def removeShackles(self) -> None:
        from ..effect.effect_shackle_tp import EffectShackleTP
        from ..effect.effect_shackle_mp import EffectShackleMP
        from ..effect.effect_shackle_agility import EffectShackleAgility
        from ..effect.effect_shackle_magic import EffectShackleMagic
        from ..effect.effect_shackle_strength import EffectShackleStrength
        from ..effect.effect_shackle_wisdom import EffectShackleWisdom
        i = 0
        while i < len(self.effects):
            effect = self.effects[i]
            if isinstance(effect, (EffectShackleTP, EffectShackleMP, EffectShackleAgility,
                                   EffectShackleMagic, EffectShackleStrength, EffectShackleWisdom)):
                effect.getCaster().removeLaunchedEffect(effect)
                self.removeEffect(effect)
                i -= 1
            i += 1

    def applyCoolDown(self) -> None:
        cooldown_copy = dict(self.mCooldown)
        for chip_id, value in cooldown_copy.items():
            if value <= 1:
                del self.mCooldown[chip_id]
            else:
                self.mCooldown[chip_id] = value - 1

    def addChip(self, chip) -> None:
        if chip is not None:
            if len(self.mChips) < self.getRAM():
                self.mChips[chip.getId()] = chip

    def addCooldown(self, chip, cooldown: int) -> None:
        from .state import State
        self.mCooldown[chip.getId()] = State.MAX_TURNS + 2 if cooldown == -1 else cooldown

    def hasCooldown(self, chipID: int) -> bool:
        return chipID in self.mCooldown

    def getCooldown(self, chipID: int) -> int:
        if not self.hasCooldown(chipID):
            return 0
        return self.mCooldown[chipID]

    def getCooldowns(self):
        return self.mCooldown

    def getFarmer(self) -> int:
        return self.mFarmer

    def getChip(self, id_: int):
        return self.mChips.get(id_)

    def getChips(self):
        return list(self.mChips.values())

    def getSkin(self) -> int:
        return self.mSkin

    def getMetal(self) -> bool:
        return self.mMetal

    def getFace(self) -> int:
        return self.mFace

    def getEffects(self):
        return self.effects

    def getLaunchedEffects(self):
        return self.launchedEffects

    def getPassiveEffects(self):
        return self.passiveEffects

    def setLevel(self, level: int) -> None:
        self.mLevel = level

    def resurrect(self, entity, factor: float, fullLife: bool) -> None:
        if fullLife:
            self.life = self.mTotalLife
        else:
            self.mTotalLife = max(10, java_round(self.mTotalLife * 0.5 * factor))
            self.life = self.mTotalLife // 2
        self.resurrected += 1
        self.endTurn()

    def useTP(self, tp: int) -> None:
        self.usedTP += tp
        self.state.statistics.useTP(tp)

    def useMP(self, mp: int) -> None:
        self.usedMP += mp
        self.state.statistics.useTP(mp)

    def __str__(self) -> str:
        return self.name

    def isAlive(self) -> bool:
        return not self.isDead()

    def isSummon(self) -> bool:
        return False

    def getSummoner(self):
        return None

    def setLife(self, life: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_LIFE, life)
        self.life = life

    def setStrength(self, strength: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_STRENGTH, strength)

    def setAgility(self, agility: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_AGILITY, agility)

    def setWisdom(self, wisdom: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_WISDOM, wisdom)

    def setResistance(self, resistance: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_RESISTANCE, resistance)

    def setScience(self, science: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_SCIENCE, science)

    def setMagic(self, magic: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_MAGIC, magic)

    def setFrequency(self, frequency: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_FREQUENCY, frequency)

    def setCores(self, cores: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_CORES, cores)

    def setRAM(self, ram: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_RAM, ram)

    def setTP(self, tp: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_TP, tp)

    def setMP(self, mp: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_MP, mp)

    def setFarmer(self, farmer: int) -> None:
        self.mFarmer = farmer

    def setFarmerName(self, name: str) -> None:
        self.mFarmerName = name

    def setFarmerCountry(self, country: str) -> None:
        self.mFarmerCountry = country

    def setAIName(self, ai: str) -> None:
        self.mAIName = ai

    def setTeamID(self, team: int) -> None:
        self.mTeamId = team

    def setTeamName(self, name: str) -> None:
        self.mTeamName = name

    def setCompositionName(self, name: str) -> None:
        self.mCompositionName = name

    def setSkin(self, skin: int) -> None:
        self.mSkin = skin

    def setHat(self, hat: int) -> None:
        self.mHat = hat

    def setMetal(self, metal: bool) -> None:
        self.mMetal = metal

    def setFace(self, face: int) -> None:
        self.mFace = face

    def getSummons(self, get_dead: bool):
        summons = []
        for e in self.state.getTeamEntities(self.getTeam(), get_dead):
            if e.isSummon() and e.getSummoner().getFId() == self.getFId():
                summons.append(e)
        return summons

    def getEntitiesAround(self, distance: int):
        entities = []
        for entity in self.state.getEntities().values():
            if entity is not self and entity.getDistance(self) <= distance:
                entities.append(entity)
        return entities

    def getDistance(self, entity) -> int:
        from ..maps.pathfinding import Pathfinding
        if self.isDead() or entity.isDead():
            return 999
        return Pathfinding.getCaseDistance(self.getCell(), entity.getCell())

    def getResurrected(self) -> int:
        return self.resurrected

    def getTotalOperations(self) -> int:
        return self.totalOperations

    def loot(self, state):
        return {}

    def setState(self, state, fid: int) -> None:
        self.state = state
        self.fight_id = fid

    def setAI(self, ai) -> None:
        self.ai = ai

    def getAI(self):
        return self.ai

    def getLogs(self):
        return self.logs

    def setLogs(self, logs) -> None:
        self.logs = logs

    def getFight(self):
        return self.fight

    def getAIFile(self):
        return self.aiFile

    def setFight(self, fight) -> None:
        self.fight = fight

    def setAIFile(self, aiFile) -> None:
        self.aiFile = aiFile

    def setRelativeShield(self, shield: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_RELATIVE_SHIELD, shield)

    def setAbsoluteShield(self, shield: int) -> None:
        self.mBaseStats.setStat(Entity.STAT_ABSOLUTE_SHIELD, shield)

    def hasState(self, state) -> bool:
        return state in self.states

    def addState(self, state) -> None:
        self.states.add(state)

    def getStates(self):
        return self.states

    def setBirthTurn(self, birthTurn: int) -> None:
        self.mBirthTurn = birthTurn

    def getBirthTurn(self) -> int:
        return self.mBirthTurn

    def addOperations(self, operations: int) -> None:
        self.totalOperations += operations

    def setInitialCell(self, cell) -> None:
        self.initialCell = cell

    def getInitialCell(self):
        return self.initialCell

    def setDead(self, dead: bool) -> None:
        if dead:
            self.life = 0

    def setOrientation(self, orientation: int) -> None:
        self.orientation = orientation

    def getOrientation(self) -> int:
        return self.orientation

    def getItemUses(self, itemID: int) -> int:
        return self.itemUses.get(itemID, 0)

    def addItemUse(self, id_: int) -> None:
        self.itemUses[id_] = self.itemUses.get(id_, 0) + 1

    def startFight(self) -> None:
        pass
