# Leek Wars Generator — Python port

A line-by-line Python translation of the official Java
[Leek Wars combat generator](https://github.com/leek-wars/leek-wars-generator),
with the LeekScript-AI runtime replaced by a plain Python interface so the
engine can be embedded directly inside Python ML training loops (PPO, CMA-ES,
neural-network self-play, …).

| | Java original | Python port |
|---|---|---|
| Source files | 173 `.java` | 188 `.py` |
| LoC (engine) | ~14 000 | ~10 100 |
| AI runtime | LeekScript bytecode | plain Python callables |
| RNG | LCG, signed-64 long | matches **bit-for-bit** |
| Determinism | yes | yes |

## Why?

The reference generator is great but couples the combat engine to a custom
LeekScript VM. For deep-learning experiments it is much more convenient to
have the rules engine *inside the same Python process* as the model: no IPC,
no JVM startup, no LeekScript compilation step. A faithful port also lets us
keep parity with the official ladder so trained agents transfer back to the
real game.

## Layout

```
leekwars_generator_python/
├── leekwars/                   # the engine (mirrors the Java package layout)
│   ├── action/                 # 30 action classes (move, damage, …)
│   ├── area/                   # 17 area shapes (single cell, circle, plus, X, …)
│   ├── attack/                 # Attack + DamageType + EntityState enums
│   ├── bulbs/, chips/, weapons/, items/, component/
│   ├── classes/                # FightClass / EntityClass / ChipClass / WeaponClass / FieldClass / NetworkClass / UtilClass — the API exposed to AIs
│   ├── effect/                 # Effect base + 56 variants (damage, heal, shackle, …)
│   ├── entity/                 # Bulb, Say
│   ├── fight/                  # Fight, FightException, FightListener, StatisticsManager
│   │   └── entity/             # EntityAI (Python AI runtime) + BulbAI
│   ├── leek/                   # Leek, Registers, RegisterManager, FarmerLog, LeekLog
│   ├── maps/                   # Cell, Map, Pathfinding, MaskAreaCell, ObstacleInfo
│   ├── outcome/                # Outcome
│   ├── scenario/               # Scenario, EntityInfo, FarmerInfo, TeamInfo
│   ├── state/                  # Entity, State, Order, StartOrder, Stats, Team
│   ├── statistics/             # StatisticsManager interface, FarmerStatistics
│   ├── turret/                 # Turret
│   ├── util/                   # json_util, util, random_generator, java_math
│   ├── censorship.py
│   ├── data.py
│   ├── error_manager.py
│   ├── fight_constants.py
│   ├── generator.py            # main entry point
│   └── log.py
├── data/                       # game data (weapons.json, chips.json, summons.json, components.json)
├── example_ai.py               # sample Python AI (port of test/ai/basic.leek)
├── run_battle.py               # CLI: run one battle with random stats
├── test_engine.py              # smoke + determinism tests
└── test_rng_vs_java.py         # bit-for-bit RNG comparison vs the Java reference
```

## Java-semantics helpers

Python's arithmetic differs from Java's in three subtle ways that matter when
the same fight has to roll the same dice. We wrap them in
`leekwars/util/java_math.py`:

| Java | Python (default) | Helper |
|---|---|---|
| `Math.round(d)` rounds half **up** | `round()` rounds half to **even** | `java_round(d)` |
| `int / int` truncates toward 0 | `int // int` rounds toward -∞ | `java_div(a, b)` |
| `int % int` keeps dividend's sign | `%` keeps divisor's sign | `java_mod(a, b)` |
| `long` overflows silently | `int` is unbounded | `java_long(n)` |

These are used everywhere the original code relies on `int`/`long`/`Math.round`
arithmetic — most importantly in the RNG and damage/heal/buff formulas.

## Validation

### RNG bit-for-bit

```bash
$ python test_rng_vs_java.py
seed=           0  OK  200/200 match
seed=           1  OK  200/200 match
seed=          42  OK  200/200 match
seed=     1234567  OK  200/200 match
seed=    99887766  OK  200/200 match
seed=          -1  OK  200/200 match
seed=         -42  OK  200/200 match
seed=  2147483647  OK  200/200 match

PASS
```

### 100 random battles & determinism

```bash
$ python test_engine.py
=== Test RNG ===
RNG seed=1234567: [0.97186279296875, 0.250274658203125, 0.7882537841796875, 0.72357177734375, 0.2124786376953125]
  -> deterministic OK

=== Test 100 random battles ===
Ran 100 random battles:
  Failures: 0
  Avg duration: 65.0
  Winners: {-1: 100, ...}

=== Test determinism ===
Map/fight determinism (seed=42):
  Same winner: True
  Same duration: True
  Same actions: True

Total failures: 0
```

## Quick start

```python
from leekwars.generator import Generator
from leekwars.scenario.scenario import Scenario
from leekwars.scenario.entity_info import EntityInfo
from leekwars.statistics.statistics_manager import DefaultStatisticsManager
from leekwars.classes import fight_class, entity_class, weapon_class


def my_ai(ai):
    """A Python AI is just a callable that drives the entity each turn."""
    enemy = fight_class.getNearestEnemy(ai)
    weapons = entity_class.getWeapons(ai)
    if weapons:
        entity_class.setWeapon(ai, weapons[0])
    fight_class.moveToward(ai, enemy)
    if enemy >= 0:
        weapon_class.useWeapon(ai, enemy)


generator = Generator(data_dir="data")
scenario = Scenario()
scenario.seed = 42
# … populate scenario.farmers / teams / entities, set entity.ai_function = my_ai
outcome = generator.runScenario(scenario, None, register_manager, statistics)
print(outcome.winner, outcome.duration)
```

A fully populated example is in [`run_battle.py`](run_battle.py).

## Writing a Python AI

A Python AI is **any callable that takes a single `ai` argument** (the
`EntityAI` instance for the entity whose turn it is). From there it has access
to the same API the Java engine exposes to LeekScript code, but as plain
Python functions:

```python
from leekwars.classes import fight_class, entity_class, weapon_class, chip_class

def my_ai(ai):
    me      = ai.getEntity()
    enemy_id = fight_class.getNearestEnemy(ai)
    enemy    = ai.getFight().getEntity(enemy_id)

    if entity_class.getLife(ai) < entity_class.getTotalLife(ai) * 0.3:
        chip_class.useChip(ai, 3)        # CHIP_BANDAGE on self

    fight_class.moveToward(ai, enemy_id)
    weapon_class.useWeapon(ai, enemy_id)
```

## Status & known gaps

- ✅ Engine: combat tick, effects, areas, actions, map, pathfinding, statistics, scenarios, RNG
- ✅ AI runtime: Python callables work in place of LeekScript bytecode
- ✅ RNG matches Java bit-for-bit
- ✅ 100 random battles run without crashing, results are deterministic
- ⚠ Statistics manager is a no-op by default; plug your own for real metrics
- ⚠ `analyzeAI` / LeekScript compilation isn't ported (intentional — Python AIs don't need it)
- ⚠ Map drawing (Swing UI in Java) isn't ported
- ⚠ `LocalDB`, `LocalDbResolver`, etc. (LeekScript test harness) aren't ported

## License

The translated engine is GPLv3 (same as upstream). New auxiliary files
(README, test runners, helpers) are MIT — see [`LICENSE`](LICENSE).

Upstream: <https://github.com/leek-wars/leek-wars-generator>
