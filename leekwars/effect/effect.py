import copy
import math
from ..util.java_math import java_round
from ..state.entity import Entity


class Effect:
    # Effect type constants
    TYPE_DAMAGE = 1
    TYPE_HEAL = 2
    TYPE_BUFF_STRENGTH = 3
    TYPE_BUFF_AGILITY = 4
    TYPE_RELATIVE_SHIELD = 5
    TYPE_ABSOLUTE_SHIELD = 6
    TYPE_BUFF_MP = 7
    TYPE_BUFF_TP = 8
    TYPE_DEBUFF = 9
    TYPE_TELEPORT = 10
    TYPE_PERMUTATION = 11
    TYPE_VITALITY = 12
    TYPE_POISON = 13
    TYPE_SUMMON = 14
    TYPE_RESURRECT = 15
    TYPE_KILL = 16
    TYPE_SHACKLE_MP = 17
    TYPE_SHACKLE_TP = 18
    TYPE_SHACKLE_STRENGTH = 19
    TYPE_DAMAGE_RETURN = 20
    TYPE_BUFF_RESISTANCE = 21
    TYPE_BUFF_WISDOM = 22
    TYPE_ANTIDOTE = 23
    TYPE_SHACKLE_MAGIC = 24
    TYPE_AFTEREFFECT = 25
    TYPE_VULNERABILITY = 26
    TYPE_ABSOLUTE_VULNERABILITY = 27
    TYPE_LIFE_DAMAGE = 28
    TYPE_STEAL_ABSOLUTE_SHIELD = 29
    TYPE_NOVA_DAMAGE = 30
    TYPE_RAW_BUFF_MP = 31
    TYPE_RAW_BUFF_TP = 32
    TYPE_POISON_TO_SCIENCE = 33
    TYPE_DAMAGE_TO_ABSOLUTE_SHIELD = 34
    TYPE_DAMAGE_TO_STRENGTH = 35
    TYPE_NOVA_DAMAGE_TO_MAGIC = 36
    TYPE_RAW_ABSOLUTE_SHIELD = 37
    TYPE_RAW_BUFF_STRENGTH = 38
    TYPE_RAW_BUFF_MAGIC = 39
    TYPE_RAW_BUFF_SCIENCE = 40
    TYPE_RAW_BUFF_AGILITY = 41
    TYPE_RAW_BUFF_RESISTANCE = 42
    TYPE_PROPAGATION = 43
    TYPE_RAW_BUFF_WISDOM = 44
    TYPE_NOVA_VITALITY = 45
    TYPE_ATTRACT = 46
    TYPE_SHACKLE_AGILITY = 47
    TYPE_SHACKLE_WISDOM = 48
    TYPE_REMOVE_SHACKLES = 49
    TYPE_MOVED_TO_MP = 50
    TYPE_PUSH = 51
    TYPE_RAW_BUFF_POWER = 52
    TYPE_REPEL = 53
    TYPE_RAW_RELATIVE_SHIELD = 54
    TYPE_ALLY_KILLED_TO_AGILITY = 55
    TYPE_KILL_TO_TP = 56
    TYPE_RAW_HEAL = 57
    TYPE_CRITICAL_TO_HEAL = 58
    TYPE_ADD_STATE = 59
    TYPE_TOTAL_DEBUFF = 60
    TYPE_STEAL_LIFE = 61
    TYPE_MULTIPLY_STATS = 62

    # Target filters constants
    TARGET_ENEMIES = 1
    TARGET_ALLIES = 2
    TARGET_CASTER = 4
    TARGET_NON_SUMMONS = 8
    TARGET_SUMMONS = 16

    # Modifiers
    MODIFIER_STACKABLE = 1
    MODIFIER_MULTIPLIED_BY_TARGETS = 2
    MODIFIER_ON_CASTER = 4
    MODIFIER_NOT_REPLACEABLE = 8
    MODIFIER_IRREDUCTIBLE = 16

    # Power in case of critical hit
    CRITICAL_FACTOR = 1.3

    # Erosion rates
    EROSION_DAMAGE = 0.05
    EROSION_POISON = 0.10
    EROSION_CRITICAL_BONUS = 0.10

    # Will be populated after all Effect subclasses are loaded
    effects = None

    def __init__(self):
        from ..state.stats import Stats
        self._id = 0
        self.turns = 0
        self.aoe = 1.0
        self.value1 = 0.0
        self.value2 = 0.0
        self.critical = False
        self.criticalPower = 1.0
        self.caster = None
        self.target = None
        self.attack = None
        self.jet = 0.0
        self.stats = Stats()
        self.logID = 0
        self.erosionRate = 0.0
        self.value = 0
        self.previousEffectTotalValue = 0
        self.targetCount = 0
        self.propagate = 0
        self.modifiers = 0
        self.state = None

    @staticmethod
    def createEffect(state, id, turns, aoe, value1, value2, critical, target, caster, attack, jet, stackable, previousEffectTotalValue, targetCount, propagate, modifiers):
        from ..action.action_add_effect import ActionAddEffect
        from ..action.action_stack_effect import ActionStackEffect

        # Invalid effect id
        if id < 0 or id > len(Effect.effects):
            return 0

        # Create the effect
        try:
            cls = Effect.effects[id - 1]
            if cls is None:
                return 0
            effect = cls()
        except Exception:
            return 0
        effect.setId(id)
        effect.turns = turns
        effect.aoe = aoe
        effect.value1 = value1
        effect.value2 = value2
        effect.critical = critical
        effect.criticalPower = Effect.CRITICAL_FACTOR if critical else 1.0
        effect.caster = caster
        effect.target = target
        effect.attack = attack
        effect.jet = jet
        effect.erosionRate = Effect.EROSION_POISON if id == Effect.TYPE_POISON else Effect.EROSION_DAMAGE
        if critical:
            effect.erosionRate += Effect.EROSION_CRITICAL_BONUS
        effect.previousEffectTotalValue = previousEffectTotalValue
        effect.targetCount = targetCount
        effect.propagate = propagate
        effect.modifiers = modifiers

        # Remove previous effect of the same type (that is not stackable)
        if effect.getTurns() != 0:
            if not stackable:
                effects = target.getEffects()
                for i in range(len(effects)):
                    e = effects[i]
                    same_attack = (e.attack is None and attack is None) or (attack is not None and e.attack is not None and e.attack.getItemId() == attack.getItemId())
                    if e.getId() == id and same_attack:
                        e.getCaster().removeLaunchedEffect(e)
                        target.removeEffect(e)
                        break
        # Compute the effect
        effect.apply(state)

        # Stack to previous item with the same characteristics
        if effect.value > 0:
            for e in target.getEffects():
                same_attack = (e.attack is None and attack is None) or (attack is not None and e.attack is not None and e.attack.getItemId() == attack.getItemId())
                if same_attack and e.getId() == id and e.turns == turns and e.caster is caster:
                    e.mergeWith(effect)
                    state.getActions().log(ActionStackEffect(e.getLogID(), effect.value))
                    return effect.value

        # Add effect to the target and the caster
        if effect.getTurns() != 0 and effect.value > 0:
            target.addEffect(effect)
            caster.addLaunchedEffect(effect)
            effect.addLog(state)
            state.statistics.effect(target, caster, effect)
        return effect.value

    def getId(self) -> int:
        return self._id

    def setId(self, id: int) -> None:
        self._id = id

    def addLog(self, state) -> None:
        from ..action.action_add_effect import ActionAddEffect
        from ..attack.attack_constants import ATTACK_TYPE_CHIP
        if self.turns == 0:
            return
        attack_type = ATTACK_TYPE_CHIP if self.attack is None else self.attack.getType()
        item_id = 0 if self.attack is None else self.attack.getItemId()
        self.logID = ActionAddEffect.createEffect(state.getActions(), attack_type, item_id, self.caster, self.target, self.getId(), self.value, self.turns, self.modifiers)

    def getStats(self):
        return self.stats

    def getID(self) -> int:
        return self.getId()

    def getLogID(self) -> int:
        return self.logID

    def isCritical(self) -> bool:
        return self.critical

    def getTurns(self) -> int:
        return self.turns

    def setTurns(self, turns: int) -> None:
        self.turns = turns

    def getAOE(self) -> float:
        return self.aoe

    def getValue(self) -> int:
        return self.value

    def getValue1(self) -> float:
        return self.value1

    def getValue2(self) -> float:
        return self.value2

    def getCaster(self):
        return self.caster

    def getTarget(self):
        return self.target

    def getAttack(self):
        return self.attack

    def getModifiers(self) -> int:
        return self.modifiers

    def reduce(self, percent: float, caster) -> None:
        reduction = max(0.0, 1.0 - percent)
        self.value = java_round(float(self.value) * reduction)
        for stat_key, stat_value in list(self.stats.stats.items()):
            sign = (1 if stat_value > 0 else (-1 if stat_value < 0 else 0))
            newValue = java_round(abs(stat_value) * reduction * sign)
            delta = newValue - stat_value
            self.stats.updateStat(stat_key, delta)
            self.target.updateBuffStats(stat_key, delta, caster)

    def mergeWith(self, effect) -> None:
        self.value += effect.value
        for stat_key, stat_value in list(self.stats.stats.items()):
            signum = 1 if stat_value > 0 else -1
            self.stats.updateStat(stat_key, effect.value * signum)

    # Abstract methods
    def apply(self, state) -> None:
        pass

    def applyStartTurn(self, state) -> None:
        pass

    @staticmethod
    def getEffectStat(type_: int) -> int:
        if type_ == Effect.TYPE_DAMAGE:
            return Entity.STAT_STRENGTH
        elif type_ in (Effect.TYPE_POISON, Effect.TYPE_SHACKLE_MAGIC, Effect.TYPE_SHACKLE_STRENGTH, Effect.TYPE_SHACKLE_MP, Effect.TYPE_SHACKLE_TP):
            return Entity.STAT_MAGIC
        elif type_ == Effect.TYPE_LIFE_DAMAGE:
            return Entity.STAT_LIFE
        elif type_ in (Effect.TYPE_NOVA_DAMAGE, Effect.TYPE_BUFF_AGILITY, Effect.TYPE_BUFF_STRENGTH, Effect.TYPE_BUFF_MP, Effect.TYPE_BUFF_TP, Effect.TYPE_BUFF_RESISTANCE, Effect.TYPE_BUFF_WISDOM):
            return Entity.STAT_SCIENCE
        elif type_ == Effect.TYPE_DAMAGE_RETURN:
            return Entity.STAT_AGILITY
        elif type_ in (Effect.TYPE_HEAL, Effect.TYPE_VITALITY):
            return Entity.STAT_WISDOM
        elif type_ in (Effect.TYPE_RELATIVE_SHIELD, Effect.TYPE_ABSOLUTE_SHIELD):
            return Entity.STAT_RESISTANCE
        return -1

    def clone(self):
        # ``copy.copy`` is ~5x slower because it goes through
        # ``__reduce_ex__`` / dict introspection. State cloning calls
        # us once per (entity, active effect), so we hand-roll the copy.
        new = self.__class__.__new__(self.__class__)
        d = new.__dict__
        d.update(self.__dict__)
        # ``stats`` is the only mutable attribute that needs its own
        # copy (everything else is either immutable or shared by ref).
        from ..state.stats import Stats
        d["stats"] = Stats(self.stats)
        return new

    def setTarget(self, entity) -> None:
        self.target = entity

    def setCaster(self, entity) -> None:
        self.caster = entity

    def getItem(self):
        return self.attack.getItem() if self.attack is not None else None

    def getState(self):
        return self.state
