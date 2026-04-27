"""Benchmark the Python engine.

Measures:
  - whole-fight throughput (random scenarios with the basic AI)
  - per-turn cost
  - per "primitive" cost (RNG draw, A* pathfinding, useWeapon)
"""

import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import leekwars.effect  # populate Effect.effects
from leekwars.generator import Generator
from leekwars.scenario.scenario import Scenario
from leekwars.scenario.farmer_info import FarmerInfo
from leekwars.scenario.team_info import TeamInfo
from leekwars.scenario.entity_info import EntityInfo
from leekwars.statistics.statistics_manager import DefaultStatisticsManager
from leekwars.leek.register_manager import RegisterManager
from leekwars.state.state import _DefaultRandom, State
from leekwars.classes import fight_class, entity_class, weapon_class

import random


class _Stats(DefaultStatisticsManager):
    def setGeneratorFight(self, fight): self._fight = fight


class _Reg(RegisterManager):
    def getRegisters(self, leek): return None
    def saveRegisters(self, leek, registers, is_new): pass


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


def make_scenario(seed: int) -> Scenario:
    rng = random.Random(seed)
    s = Scenario()
    s.seed = seed
    s.maxTurns = 64
    s.type = State.TYPE_SOLO
    s.context = State.CONTEXT_TEST
    f1 = FarmerInfo(); f1.id = 1; f1.name = "P1"; f1.country = "fr"
    f2 = FarmerInfo(); f2.id = 2; f2.name = "P2"; f2.country = "fr"
    s.farmers[1] = f1; s.farmers[2] = f2
    t1 = TeamInfo(); t1.id = 1; t1.name = "A"
    t2 = TeamInfo(); t2.id = 2; t2.name = "B"
    s.teams[1] = t1; s.teams[2] = t2
    for team_id, farmer_id, name in [(1, 1, "A"), (2, 2, "B")]:
        e = EntityInfo()
        e.id = team_id * 10
        e.name = name
        e.type = 0
        e.farmer = farmer_id
        e.team = team_id
        e.level = rng.randint(80, 200)
        e.life = rng.randint(2000, 4000)
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
        e.weapons = [37]   # pistol — keeps the fight simple but realistic
        e.chips = []
        e.ai_function = _basic_ai
        s.addEntity(team_id - 1, e)
    return s


def bench_full_fights(generator, n=200):
    times = []
    durations = []
    actions_total = 0
    t0 = time.perf_counter()
    for seed in range(1, n + 1):
        s = make_scenario(seed)
        t = time.perf_counter()
        outcome = generator.runScenario(s, None, _Reg(), _Stats())
        times.append(time.perf_counter() - t)
        durations.append(outcome.duration)
        if outcome.fight is not None:
            actions_total += len(outcome.fight.actions)
    total = time.perf_counter() - t0
    return {
        "fights": n,
        "wallclock_s": total,
        "fights_per_sec": n / total,
        "ms_per_fight_avg": 1000 * statistics.mean(times),
        "ms_per_fight_p50": 1000 * statistics.median(times),
        "ms_per_fight_p95": 1000 * sorted(times)[int(0.95 * n)],
        "avg_turns": statistics.mean(durations),
        "avg_actions_per_fight": actions_total / n,
        "actions_per_sec": actions_total / total,
    }


def bench_rng(n=1_000_000):
    rng = _DefaultRandom()
    rng.seed(42)
    t = time.perf_counter()
    for _ in range(n):
        rng.get_double()
    dt = time.perf_counter() - t
    return {"rng_per_sec": n / dt, "ns_per_call": 1e9 * dt / n}


def bench_pathfinding(generator, n=1000):
    """A* between random pairs of cells on a fresh map."""
    s = make_scenario(seed=999)
    outcome = generator.runScenario(s, None, _Reg(), _Stats())
    # Grab the fight so we have a populated map. We can't rerun A* on the
    # finished fight directly, so build a fresh one.
    s2 = make_scenario(seed=888)
    from leekwars.fight.fight import Fight
    fight = Fight(generator)
    fight.getState().setRegisterManager(_Reg())
    fight.setStatisticsManager(_Stats())
    fight.setMaxTurns(64)
    fight.getState().setType(State.TYPE_SOLO)
    fight.getState().setContext(State.CONTEXT_TEST)
    fight.getState().seed(888)
    t = 0
    from leekwars.leek.farmer_log import FarmerLog
    from leekwars.leek.leek_log import LeekLog
    from leekwars.fight.entity.entity_ai import EntityAI
    logs = {}
    for team in s2.entities:
        for ei in team:
            if ei.aiOwner not in logs:
                logs[ei.aiOwner] = FarmerLog(fight, ei.farmer)
            entity = ei.createEntity(generator, s2, fight)
            fight.getState().addEntity(t, entity)
            entity.setFight(fight)
            entity.setLogs(LeekLog(logs[ei.aiOwner], entity))
            entity.setAIFile(EntityAI.resolve(generator, ei, entity))
        t += 1
    fight.initFight()
    m = fight.getState().getMap()
    cells = [c for c in m.getCells() if c.isWalkable()]
    rng = random.Random(0)
    times = []
    for _ in range(n):
        a = rng.choice(cells)
        b = rng.choice(cells)
        t = time.perf_counter()
        m.getAStarPath(a, [b], None)
        times.append(time.perf_counter() - t)
    return {"astar_calls": n, "ms_per_call": 1000 * statistics.mean(times)}


def main():
    print("Loading generator…")
    g = Generator(data_dir=os.path.join(os.path.dirname(__file__), "data"))

    print("\n=== RNG ===")
    r = bench_rng()
    print(f"  {r['rng_per_sec']:>12,.0f} draws/sec   ({r['ns_per_call']:.0f} ns/call)")

    print("\n=== A* pathfinding ===")
    p = bench_pathfinding(g, n=500)
    print(f"  {p['astar_calls']} runs, {p['ms_per_call']:.2f} ms/call")

    print("\n=== Full fights (basic AI vs basic AI) ===")
    f = bench_full_fights(g, n=200)
    print(f"  {f['fights']} fights in {f['wallclock_s']:.2f}s")
    print(f"  {f['fights_per_sec']:>10.1f} fights/sec")
    print(f"  {f['ms_per_fight_avg']:>10.1f} ms/fight (avg)")
    print(f"  {f['ms_per_fight_p50']:>10.1f} ms/fight (p50)")
    print(f"  {f['ms_per_fight_p95']:>10.1f} ms/fight (p95)")
    print(f"  {f['avg_turns']:>10.1f} turns/fight (avg)")
    print(f"  {f['avg_actions_per_fight']:>10.1f} actions/fight (avg)")
    print(f"  {f['actions_per_sec']:>10,.0f} actions/sec")


if __name__ == "__main__":
    main()
