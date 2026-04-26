"""Quick smoke tests for the Python generator.

Doesn't use the Java generator directly — checks deterministic invariants
(RNG sequence, map generation, basic combat math) that any line-by-line
port should preserve.
"""

import sys

from leekwars.state.state import _DefaultRandom


def test_rng_sequence():
    """Java's LCG produces a known sequence with the same seed."""
    rng = _DefaultRandom()
    rng.seed(1234567)
    out = [rng.get_double() for _ in range(5)]
    print("RNG seed=1234567:", out)

    # Java reference (computed by running the same algorithm in Java):
    # n = n * 1103515245 + 12345 (long), r = (n / 65536) % 32768 + 32768, return r/65536
    expected = []  # We don't have Java values handy, but the computation should be deterministic.
    # Just verify it's deterministic
    rng2 = _DefaultRandom()
    rng2.seed(1234567)
    out2 = [rng2.get_double() for _ in range(5)]
    assert out == out2, f"RNG not deterministic: {out} vs {out2}"
    print("  -> deterministic OK")


def test_random_battles():
    """Run many random battles and ensure none crash."""
    import random
    from run_battle import make_random_scenario, FightStats, NoopRegisterManager
    from leekwars.generator import Generator

    generator = Generator(data_dir="data")
    failures = 0
    durations = []
    winners = {-1: 0, -2: 0, 0: 0, 1: 0}
    for seed in range(100, 200):
        scenario = make_random_scenario(seed)
        outcome = generator.runScenario(scenario, None, NoopRegisterManager(), FightStats())
        if outcome.exception is not None:
            print(f"FAIL seed={seed}: {outcome.exception}")
            failures += 1
            continue
        durations.append(outcome.duration)
        winners[outcome.winner] = winners.get(outcome.winner, 0) + 1
    print(f"\nRan 100 random battles:")
    print(f"  Failures: {failures}")
    print(f"  Avg duration: {sum(durations) / len(durations) if durations else 0:.1f}")
    print(f"  Winners: {winners}")
    return failures


def test_map_consistency():
    """Map generation should be deterministic for a given seed/teams."""
    from run_battle import make_random_scenario, FightStats, NoopRegisterManager
    from leekwars.generator import Generator

    generator = Generator(data_dir="data")
    out_a = generator.runScenario(make_random_scenario(42), None, NoopRegisterManager(), FightStats())
    out_b = generator.runScenario(make_random_scenario(42), None, NoopRegisterManager(), FightStats())
    actions_a = out_a.fight.toJSON()
    actions_b = out_b.fight.toJSON()
    same_winner = out_a.winner == out_b.winner
    same_duration = out_a.duration == out_b.duration
    same_actions = actions_a == actions_b
    print(f"\nMap/fight determinism (seed=42):")
    print(f"  Same winner: {same_winner}")
    print(f"  Same duration: {same_duration}")
    print(f"  Same actions: {same_actions}")
    return 0 if (same_winner and same_duration and same_actions) else 1


def main():
    print("=== Test RNG ===")
    test_rng_sequence()
    print("\n=== Test 100 random battles ===")
    f1 = test_random_battles()
    print("\n=== Test determinism ===")
    f2 = test_map_consistency()
    failures = f1 + f2
    print(f"\nTotal failures: {failures}")
    sys.exit(failures)


if __name__ == "__main__":
    main()
