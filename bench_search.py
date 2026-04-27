"""Benchmark the BFS-dim-1 hot path:

  for each candidate action:
      clone state
      apply action
      score (placeholder = read a few fields)
"""

import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import leekwars.effect
from leekwars.generator import Generator
from leekwars.state.state import State
from bench import _Reg, _Stats, make_scenario


def setup_state(seed=42):
    g = Generator(data_dir=os.path.join(os.path.dirname(__file__), "data"))
    s = make_scenario(seed)
    # Build a Fight up to its first decision point
    from leekwars.fight.fight import Fight
    from leekwars.leek.farmer_log import FarmerLog
    from leekwars.leek.leek_log import LeekLog
    from leekwars.fight.entity.entity_ai import EntityAI
    fight = Fight(g, listener=None)
    st = fight.getState()
    st.setRegisterManager(_Reg())
    fight.setStatisticsManager(_Stats())
    fight.setMaxTurns(64)
    st.setType(s.type)
    st.setContext(s.context)
    st.seed(s.seed)
    logs = {}
    t = 0
    for team in s.entities:
        for ei in team:
            if ei.aiOwner not in logs:
                logs[ei.aiOwner] = FarmerLog(fight, ei.farmer)
            entity = ei.createEntity(g, s, fight)
            st.addEntity(t, entity)
            entity.setFight(fight)
            entity.setLogs(LeekLog(logs[ei.aiOwner], entity))
            entity.setAIFile(EntityAI.resolve(g, ei, entity))
        t += 1
    fight.initFight()
    for entity in st.getEntities().values():
        ai_function = entity.getAIFile()
        ai = EntityAI.build(g, ai_function, entity)
        entity.setAI(ai)
        ai.setFight(fight)
        st.statistics.init(entity)
        st.statistics.characteristics(entity)
        entity.startFight()
    return fight, st


def bench_clone(state, n=1000):
    times = []
    for _ in range(n):
        t = time.perf_counter()
        clone = State(state)
        times.append(time.perf_counter() - t)
    return {"calls": n, "ms_avg": 1000 * statistics.mean(times), "us_avg": 1e6 * statistics.mean(times)}


def bench_apply_use_weapon(state, n=1000):
    """Cost of: clone, equip weapon, useWeapon, read HPs."""
    from leekwars.weapons import weapons as Weapons
    cur = state.getOrder().current()
    weapon = Weapons.getWeapon(cur.getWeapons()[0].getId())
    enemies = [e for e in state.getEntities().values() if e.getTeam() != cur.getTeam() and e.isAlive()]
    target_cell = enemies[0].getCell()
    times = []
    for _ in range(n):
        t = time.perf_counter()
        c = State(state)
        cur2 = c.getOrder().current()
        c.setWeapon(cur2, weapon)
        c.useWeapon(cur2, target_cell)
        # read scoring inputs
        for e in c.getEntities().values():
            _ = (e.getLife(), e.getCell())
        times.append(time.perf_counter() - t)
    return {"calls": n, "ms_avg": 1000 * statistics.mean(times), "us_avg": 1e6 * statistics.mean(times)}


def bench_apply_move(state, n=1000):
    cur = state.getOrder().current()
    m = state.getMap()
    # Pick a reachable cell
    enemies = [e for e in state.getEntities().values() if e.getTeam() != cur.getTeam() and e.isAlive()]
    target = enemies[0].getCell()
    path = m.getPathBeetween(cur.getCell(), target, None)
    times = []
    for _ in range(n):
        t = time.perf_counter()
        c = State(state)
        cur2 = c.getOrder().current()
        used_path = path[:cur2.getMP()] if path else []
        c.moveEntity(cur2, used_path)
        for e in c.getEntities().values():
            _ = (e.getLife(), e.getCell())
        times.append(time.perf_counter() - t)
    return {"calls": n, "ms_avg": 1000 * statistics.mean(times), "us_avg": 1e6 * statistics.mean(times)}


def main():
    print("Setting up a mid-fight state…")
    _, state = setup_state(seed=42)

    print("\n=== State clone (deep copy of fight state) ===")
    r = bench_clone(state, n=2000)
    print(f"  {r['us_avg']:.1f} µs/clone   ({r['calls']} runs)")

    print("\n=== Clone + setWeapon + useWeapon + read ===")
    r = bench_apply_use_weapon(state, n=2000)
    print(f"  {r['us_avg']:.1f} µs/iteration")
    print(f"  ->> {1e6 / r['us_avg']:.0f} action evaluations/sec")

    print("\n=== Clone + moveEntity + read ===")
    r = bench_apply_move(state, n=2000)
    print(f"  {r['us_avg']:.1f} µs/iteration")
    print(f"  ->> {1e6 / r['us_avg']:.0f} action evaluations/sec")


if __name__ == "__main__":
    main()
