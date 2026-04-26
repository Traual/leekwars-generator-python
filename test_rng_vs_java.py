"""Compare the Python RNG against the Java implementation across many seeds.

Requires the small Java helper at ``java_reference/TestRng.java`` to be
compiled (``javac TestRng.java`` once).
"""

import os
import subprocess
import sys

from leekwars.state.state import _DefaultRandom


JAVA_REF = os.path.join(os.path.dirname(__file__), "java_reference")


def java_rng(seed: int, n: int) -> list:
    out = subprocess.check_output(["java", "-cp", JAVA_REF, "TestRng", str(seed), str(n)],
                                  stderr=subprocess.STDOUT, text=True)
    return [float(line) for line in out.strip().splitlines()]


def python_rng(seed: int, n: int) -> list:
    rng = _DefaultRandom()
    rng.seed(seed)
    return [rng.get_double() for _ in range(n)]


def main():
    failures = 0
    for seed in [0, 1, 42, 1234567, 99887766, -1, -42, 2147483647]:
        java = java_rng(seed, 200)
        py = python_rng(seed, 200)
        if java == py:
            print(f"seed={seed:>12d}  OK  200/200 match")
        else:
            diffs = sum(1 for a, b in zip(java, py) if a != b)
            print(f"seed={seed:>12d}  XX  {diffs}/200 differ")
            for i, (a, b) in enumerate(zip(java, py)):
                if a != b:
                    print(f"  index {i}: java={a}  python={b}")
                    if i > 5:
                        break
            failures += 1
    print()
    print("PASS" if failures == 0 else f"FAIL ({failures} seeds differ)")
    sys.exit(failures)


if __name__ == "__main__":
    main()
