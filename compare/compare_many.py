"""Run many random scenarios through both engines and assert byte-for-byte equality.

Generates random stats and seeds, writes a temporary scenario.json, runs both
engines, and reports per-seed how many actions differ.
"""

import json
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import leekwars.effect  # populate Effect.effects table
from leekwars.generator import Generator
from leekwars.scenario.scenario import Scenario
from leekwars.statistics.statistics_manager import DefaultStatisticsManager
from leekwars.leek.register_manager import RegisterManager
from python_basic_ai import basic_ai


JAVA_GEN_DIR = "C:/Users/aurel/Desktop/Training Weights Leekwars/Leekwars-Tools/leek-wars-generator"
HERE = os.path.dirname(os.path.abspath(__file__))


class _Stats(DefaultStatisticsManager):
    def setGeneratorFight(self, fight):
        self._fight = fight


class _Reg(RegisterManager):
    def getRegisters(self, leek):
        return None
    def saveRegisters(self, leek, registers, is_new):
        pass


def make_scenario(seed: int, ai_path: str = "test/ai/basic.leek") -> dict:
    rng = random.Random(seed)

    def entity(eid, team, farmer, cell):
        return {
            "id": eid,
            "ai": ai_path,
            "name": f"E{eid}",
            "type": 0,
            "farmer": farmer,
            "team": team,
            "level": rng.randint(50, 200),
            "life": rng.randint(1500, 4000),
            "strength": rng.randint(100, 400),
            "agility": rng.randint(0, 200),
            "wisdom": rng.randint(0, 100),
            "resistance": rng.randint(0, 200),
            "science": rng.randint(0, 100),
            "magic": rng.randint(0, 100),
            "frequency": rng.randint(50, 150),
            "cores": 10,
            "ram": 10,
            "tp": rng.randint(10, 18),
            "mp": rng.randint(4, 8),
            "cell": cell,
            "weapons": [37],
            "chips": [],
        }

    return {
        "farmers": [
            {"id": 1, "name": "P1", "country": "fr"},
            {"id": 2, "name": "P2", "country": "fr"},
        ],
        "teams": [
            {"id": 1, "name": "TeamA"},
            {"id": 2, "name": "TeamB"},
        ],
        "entities": [
            [entity(1, 1, 1, rng.randint(50, 250))],
            [entity(2, 2, 2, rng.randint(350, 550))],
        ],
        "random_seed": seed,
        "max_turns": 64,
    }


def run_python(scenario_path: str) -> dict:
    scenario = Scenario.fromFile(scenario_path)
    for team in scenario.entities:
        for entity in team:
            entity.ai_function = basic_ai
    generator = Generator(data_dir=os.path.join(HERE, "data"))
    outcome = generator.runScenario(scenario, None, _Reg(), _Stats())
    return {
        "winner": outcome.winner,
        "duration": outcome.duration,
        "actions": outcome.fight.toJSON()["actions"] if outcome.fight else [],
    }


def run_java(scenario_path: str) -> dict:
    proc = subprocess.run(["java", "-jar", "generator.jar", scenario_path],
                          cwd=JAVA_GEN_DIR, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    raw = json.loads(proc.stdout)
    return {
        "winner": raw["winner"],
        "duration": raw["duration"],
        "actions": raw["fight"]["actions"],
    }


def main():
    seeds = [int(x) for x in sys.argv[1:]] or [42, 100, 200, 333, 500, 777, 1234, 99999]
    scenario_path = os.path.join(HERE, "_tmp_scenario.json")

    pass_count = 0
    fail_count = 0
    for seed in seeds:
        scenario = make_scenario(seed)
        with open(scenario_path, "w") as f:
            json.dump(scenario, f)

        try:
            j = run_java(scenario_path)
            p = run_python(scenario_path)
        except Exception as e:
            print(f"seed={seed:>10d}  ERROR  {e}")
            fail_count += 1
            continue

        same_winner = j["winner"] == p["winner"]
        same_duration = j["duration"] == p["duration"]
        n = min(len(j["actions"]), len(p["actions"]))
        diffs = sum(1 for a, b in zip(j["actions"], p["actions"]) if a != b)
        same_len = len(j["actions"]) == len(p["actions"])

        ok = same_winner and same_duration and same_len and diffs == 0
        if ok:
            print(f"seed={seed:>10d}  OK   actions={len(j['actions'])} winner={j['winner']} duration={j['duration']}")
            pass_count += 1
        else:
            mismatches = []
            if not same_winner:
                mismatches.append(f"winner J={j['winner']} P={p['winner']}")
            if not same_duration:
                mismatches.append(f"duration J={j['duration']} P={p['duration']}")
            if not same_len:
                mismatches.append(f"len J={len(j['actions'])} P={len(p['actions'])}")
            if diffs:
                mismatches.append(f"{diffs}/{n} actions differ")
            print(f"seed={seed:>10d}  FAIL {' | '.join(mismatches)}")
            # Show first 3 differing actions
            shown = 0
            for i in range(n):
                if j["actions"][i] != p["actions"][i] and shown < 3:
                    print(f"   [{i}] J: {j['actions'][i]}\n       P: {p['actions'][i]}")
                    shown += 1
            fail_count += 1

    if os.path.exists(scenario_path):
        os.remove(scenario_path)

    print(f"\n{pass_count}/{pass_count + fail_count} scenarios match Java byte-for-byte")
    sys.exit(fail_count)


if __name__ == "__main__":
    main()
