"""cProfile a batch of fights to find the real bottlenecks."""

import cProfile
import io
import os
import pstats
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bench import _basic_ai, _Reg, _Stats, make_scenario
import leekwars.effect
from leekwars.generator import Generator


def run(g, n=100):
    for seed in range(1, n + 1):
        g.runScenario(make_scenario(seed), None, _Reg(), _Stats())


def main():
    g = Generator(data_dir=os.path.join(os.path.dirname(__file__), "data"))
    pr = cProfile.Profile()
    pr.enable()
    run(g, 100)
    pr.disable()

    s = io.StringIO()
    pstats.Stats(pr, stream=s).strip_dirs().sort_stats("cumulative").print_stats(25)
    print(s.getvalue())


if __name__ == "__main__":
    main()
