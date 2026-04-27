"""How fast can we run fights when we throw all CPU cores at the problem?"""

import multiprocessing as mp
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _worker(seed_chunk):
    # Each worker loads the generator once, then crunches its chunk.
    import leekwars.effect
    from leekwars.generator import Generator
    from bench import make_scenario, _Reg, _Stats

    g = Generator(data_dir=os.path.join(os.path.dirname(__file__), "data"))
    n = 0
    for s in seed_chunk:
        g.runScenario(make_scenario(s), None, _Reg(), _Stats())
        n += 1
    return n


def main():
    n_fights = 1000
    cores = mp.cpu_count()
    seeds = list(range(1, n_fights + 1))
    chunks = [seeds[i::cores] for i in range(cores)]

    t = time.perf_counter()
    with mp.Pool(cores) as pool:
        results = pool.map(_worker, chunks)
    dt = time.perf_counter() - t

    total = sum(results)
    print(f"{cores} cores, {total} fights in {dt:.2f}s")
    print(f"  {total / dt:.0f} fights/sec ({1000 * dt / total:.2f} ms/fight)")


if __name__ == "__main__":
    main()
