"""Effect package — exposes the full effect class table after all variants are imported."""

from .effect import Effect

# Mirrors the Java ``Effect.effects`` static array (1-indexed, gaps allowed).
from .effect_damage import EffectDamage
from .effect_heal import EffectHeal
from .effect_buff_strength import EffectBuffStrength
from .effect_buff_agility import EffectBuffAgility
from .effect_relative_shield import EffectRelativeShield
from .effect_absolute_shield import EffectAbsoluteShield
from .effect_buff_mp import EffectBuffMP
from .effect_buff_tp import EffectBuffTP
from .effect_debuff import EffectDebuff
from .effect_teleport import EffectTeleport
from .effect_permutation import EffectPermutation
from .effect_vitality import EffectVitality
from .effect_poison import EffectPoison
from .effect_summon import EffectSummon
from .effect_resurrect import EffectResurrect
from .effect_kill import EffectKill
from .effect_shackle_mp import EffectShackleMP
from .effect_shackle_tp import EffectShackleTP
from .effect_shackle_strength import EffectShackleStrength
from .effect_damage_return import EffectDamageReturn
from .effect_buff_resistance import EffectBuffResistance
from .effect_buff_wisdom import EffectBuffWisdom
from .effect_antidote import EffectAntidote
from .effect_shackle_magic import EffectShackleMagic
from .effect_aftereffect import EffectAftereffect
from .effect_vulnerability import EffectVulnerability
from .effect_absolute_vulnerability import EffectAbsoluteVulnerability
from .effect_life_damage import EffectLifeDamage
from .effect_steal_absolute_shield import EffectStealAbsoluteShield
from .effect_nova_damage import EffectNovaDamage
from .effect_raw_buff_mp import EffectRawBuffMP
from .effect_raw_buff_tp import EffectRawBuffTP
from .effect_raw_absolute_shield import EffectRawAbsoluteShield
from .effect_raw_buff_strength import EffectRawBuffStrength
from .effect_raw_buff_magic import EffectRawBuffMagic
from .effect_raw_buff_science import EffectRawBuffScience
from .effect_raw_buff_agility import EffectRawBuffAgility
from .effect_raw_buff_resistance import EffectRawBuffResistance
from .effect_raw_buff_wisdom import EffectRawBuffWisdom
from .effect_nova_vitality import EffectNovaVitality
from .effect_attract import EffectAttract
from .effect_shackle_agility import EffectShackleAgility
from .effect_shackle_wisdom import EffectShackleWisdom
from .effect_remove_shackles import EffectRemoveShackles
from .effect_push import EffectPush
from .effect_raw_buff_power import EffectRawBuffPower
from .effect_repel import EffectRepel
from .effect_raw_relative_shield import EffectRawRelativeShield
from .effect_ally_killed_to_agility import EffectAllyKilledToAgility
from .effect_raw_heal import EffectRawHeal
from .effect_add_state import EffectAddState
from .effect_total_debuff import EffectTotalDebuff
from .effect_steal_life import EffectStealLife
from .effect_multiply_stats import EffectMultiplyStats


# Same indexing as Java's Effect.effects[] — gaps are None.
Effect.effects = [
    EffectDamage,                # 1  TYPE_DAMAGE
    EffectHeal,                  # 2  TYPE_HEAL
    EffectBuffStrength,          # 3  TYPE_BUFF_STRENGTH
    EffectBuffAgility,           # 4  TYPE_BUFF_AGILITY
    EffectRelativeShield,        # 5  TYPE_RELATIVE_SHIELD
    EffectAbsoluteShield,        # 6  TYPE_ABSOLUTE_SHIELD
    EffectBuffMP,                # 7  TYPE_BUFF_MP
    EffectBuffTP,                # 8  TYPE_BUFF_TP
    EffectDebuff,                # 9  TYPE_DEBUFF
    EffectTeleport,              # 10 TYPE_TELEPORT
    EffectPermutation,           # 11 TYPE_PERMUTATION
    EffectVitality,              # 12 TYPE_VITALITY
    EffectPoison,                # 13 TYPE_POISON
    EffectSummon,                # 14 TYPE_SUMMON
    EffectResurrect,             # 15 TYPE_RESURRECT
    EffectKill,                  # 16 TYPE_KILL
    EffectShackleMP,             # 17 TYPE_SHACKLE_MP
    EffectShackleTP,             # 18 TYPE_SHACKLE_TP
    EffectShackleStrength,       # 19 TYPE_SHACKLE_STRENGTH
    EffectDamageReturn,          # 20 TYPE_DAMAGE_RETURN
    EffectBuffResistance,        # 21 TYPE_BUFF_RESISTANCE
    EffectBuffWisdom,            # 22 TYPE_BUFF_WISDOM
    EffectAntidote,              # 23 TYPE_ANTIDOTE
    EffectShackleMagic,          # 24 TYPE_SHACKLE_MAGIC
    EffectAftereffect,           # 25 TYPE_AFTEREFFECT
    EffectVulnerability,         # 26 TYPE_VULNERABILITY
    EffectAbsoluteVulnerability, # 27 TYPE_ABSOLUTE_VULNERABILITY
    EffectLifeDamage,            # 28 TYPE_LIFE_DAMAGE
    EffectStealAbsoluteShield,   # 29 TYPE_STEAL_ABSOLUTE_SHIELD
    EffectNovaDamage,            # 30 TYPE_NOVA_DAMAGE
    EffectRawBuffMP,             # 31 TYPE_RAW_BUFF_MP
    EffectRawBuffTP,             # 32 TYPE_RAW_BUFF_TP
    None,                        # 33
    None,                        # 34
    None,                        # 35
    None,                        # 36
    EffectRawAbsoluteShield,     # 37 TYPE_RAW_ABSOLUTE_SHIELD
    EffectRawBuffStrength,       # 38 TYPE_RAW_BUFF_STRENGTH
    EffectRawBuffMagic,          # 39 TYPE_RAW_BUFF_MAGIC
    EffectRawBuffScience,        # 40 TYPE_RAW_BUFF_SCIENCE
    EffectRawBuffAgility,        # 41 TYPE_RAW_BUFF_AGILITY
    EffectRawBuffResistance,     # 42 TYPE_RAW_BUFF_RESISTANCE
    None,                        # 43 TYPE_PROPAGATION (handled inline)
    EffectRawBuffWisdom,         # 44 TYPE_RAW_BUFF_WISDOM
    EffectNovaVitality,          # 45 TYPE_NOVA_VITALITY
    EffectAttract,               # 46 TYPE_ATTRACT
    EffectShackleAgility,        # 47 TYPE_SHACKLE_AGILITY
    EffectShackleWisdom,         # 48 TYPE_SHACKLE_WISDOM
    EffectRemoveShackles,        # 49 TYPE_REMOVE_SHACKLES
    None,                        # 50 TYPE_MOVED_TO_MP (passive)
    EffectPush,                  # 51 TYPE_PUSH
    EffectRawBuffPower,          # 52 TYPE_RAW_BUFF_POWER
    EffectRepel,                 # 53 TYPE_REPEL
    EffectRawRelativeShield,     # 54 TYPE_RAW_RELATIVE_SHIELD
    None,                        # 55 TYPE_ALLY_KILLED_TO_AGILITY (passive)
    None,                        # 56 TYPE_KILL_TO_TP (passive)
    EffectRawHeal,               # 57 TYPE_RAW_HEAL
    None,                        # 58 TYPE_CRITICAL_TO_HEAL (passive)
    EffectAddState,              # 59 TYPE_ADD_STATE
    EffectTotalDebuff,           # 60 TYPE_TOTAL_DEBUFF
    EffectStealLife,             # 61 TYPE_STEAL_LIFE
    EffectMultiplyStats,         # 62 TYPE_MULTIPLY_STATS
]
