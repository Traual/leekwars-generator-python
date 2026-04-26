from abc import ABC, abstractmethod


class Action(ABC):

    # Actions
    START_FIGHT = 0
    END_FIGHT = 4
    PLAYER_DEAD = 5
    NEW_TURN = 6
    LEEK_TURN = 7
    END_TURN = 8
    SUMMON = 9
    MOVE_TO = 10
    KILL = 11
    USE_CHIP = 12
    SET_WEAPON = 13
    STACK_EFFECT = 14
    CHEST_OPENED = 15
    USE_WEAPON = 16

    # Buffs
    LOST_PT = 100
    LOST_LIFE = 101
    LOST_PM = 102
    HEAL = 103
    VITALITY = 104
    RESURRECT = 105
    LOSE_STRENGTH = 106
    NOVA_DAMAGE = 107
    DAMAGE_RETURN = 108
    LIFE_DAMAGE = 109
    POISON_DAMAGE = 110
    AFTEREFFECT = 111
    NOVA_VITALITY = 112

    # "fun" actions
    LAMA = 201
    SAY = 203
    SHOW_CELL = 205

    # Effects
    ADD_WEAPON_EFFECT = 301
    ADD_CHIP_EFFECT = 302
    REMOVE_EFFECT = 303
    UPDATE_EFFECT = 304
    REDUCE_EFFECTS = 306
    REMOVE_POISONS = 307
    REMOVE_SHACKLES = 308

    # Other
    ERROR = 1000
    MAP = 1001
    AI_ERROR = 1002

    @abstractmethod
    def getJSON(self):
        pass
