"""How many BFS-dim-1 action evaluations can we do per second across all cores?

Models the inner loop of a BFS-dim-1 search: pick a candidate action,
clone the state, apply it, read out the result.
"""

import multiprocessing as mp
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _worker(args):
    n, seed = args
    import leekwars.effect
    from leekwars.state.state import State
    from leekwars.weapons import weapons as Weapons
    from bench_search import setup_state

    _, state = setup_state(seed=seed)
    cur = state.getOrder().current()
    weapon = Weapons.getWeapon(cur.getWeapons()[0].getId())
    enemies = [e for e in state.getEntities().values() if e.getTeam() != cur.getTeam() and e.isAlive()]
    target_cell = enemies[0].getCell()

    for _ in range(n):
        c = State(state)
        cur2 = c.getOrder().current()
        c.setWeapon(cur2, weapon)
        c.useWeapon(cur2, target_cell)
        for e in c.getEntities().values():
            _ = (e.getLife(), e.getCell())
    return n


def main():
    cores = mp.cpu_count()
    n_per_core = 50_000
    args = [(n_per_core, i + 1) for i in range(cores)]
    t = time.perf_counter()
    with mp.Pool(cores) as pool:
        results = pool.map(_worker, args)
    dt = time.perf_counter() - t
    total = sum(results)
    print(f"{cores} cores * {n_per_core} evals = {total} evaluations in {dt:.2f}s")
    print(f"  {total / dt:,.0f} evals/sec")
    print(f"  {1e6 * dt / total:.1f} us/eval (effective)")


if __name__ == "__main__":
    main()
