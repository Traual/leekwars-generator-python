"""End-to-end comparison: same scenario through Java and Python generators."""

import json
import os
import subprocess
import sys

# Make the parent leekwars/ importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from leekwars.generator import Generator
from leekwars.scenario.scenario import Scenario
from leekwars.statistics.statistics_manager import DefaultStatisticsManager
from leekwars.leek.register_manager import RegisterManager
from python_basic_ai import basic_ai


SCENARIO_PATH = os.path.join(os.path.dirname(__file__), "scenario.json")
JAVA_OUT_PATH = os.path.join(os.path.dirname(__file__), "java_output.json")
PY_OUT_PATH = os.path.join(os.path.dirname(__file__), "python_output.json")
JAVA_GEN_DIR = "C:/Users/aurel/Desktop/Training Weights Leekwars/Leekwars-Tools/leek-wars-generator"


class _Stats(DefaultStatisticsManager):
    def setGeneratorFight(self, fight):
        self._fight = fight


class _Reg(RegisterManager):
    def getRegisters(self, leek):
        return None
    def saveRegisters(self, leek, registers, is_new):
        pass


def run_python():
    scenario = Scenario.fromFile(SCENARIO_PATH)
    # Wire each entity's AI to the Python equivalent of basic.leek
    for team in scenario.entities:
        for entity in team:
            entity.ai_function = basic_ai

    generator = Generator(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
    outcome = generator.runScenario(scenario, None, _Reg(), _Stats())

    out = {
        "winner": outcome.winner,
        "duration": outcome.duration,
        "actions": outcome.fight.toJSON()["actions"] if outcome.fight else [],
    }
    with open(PY_OUT_PATH, "w") as f:
        json.dump(out, f)
    return out


def run_java():
    proc = subprocess.run(["java", "-jar", "generator.jar", SCENARIO_PATH],
                          cwd=JAVA_GEN_DIR, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    raw = json.loads(proc.stdout)
    out = {
        "winner": raw["winner"],
        "duration": raw["duration"],
        "actions": raw["fight"]["actions"],
    }
    with open(JAVA_OUT_PATH, "w") as f:
        json.dump(out, f)
    return out


def normalize_action(a):
    """Bring Java + Python action representations to a comparable form."""
    return [normalize_action(x) if isinstance(x, list) else x for x in a]


def diff_actions(java, python):
    print(f"Java   : {len(java)} actions, winner {java['winner'] if isinstance(java, dict) else 'N/A'}")
    print(f"Python : {len(python)} actions")
    n = min(len(java), len(python))
    diffs = 0
    for i in range(n):
        if java[i] != python[i]:
            diffs += 1
            if diffs <= 10:
                print(f"  [{i}] java={java[i]}  python={python[i]}")
    if len(java) != len(python):
        print(f"  Length differs: java={len(java)} python={len(python)}")
    print(f"Total differing actions: {diffs} (out of {n} compared)")
    return diffs


def main():
    print("=== Java run ===")
    java = run_java()
    print(f"  winner={java['winner']}  duration={java['duration']}  actions={len(java['actions'])}")

    print("\n=== Python run ===")
    py = run_python()
    print(f"  winner={py['winner']}  duration={py['duration']}  actions={len(py['actions'])}")

    print("\n=== Comparison ===")
    print(f"  winner    : {'OK' if java['winner'] == py['winner'] else 'DIFF'} (java={java['winner']} python={py['winner']})")
    print(f"  duration  : {'OK' if java['duration'] == py['duration'] else 'DIFF'} (java={java['duration']} python={py['duration']})")

    diffs = diff_actions(java['actions'], py['actions'])
    sys.exit(0 if (diffs == 0 and java['winner'] == py['winner'] and java['duration'] == py['duration']) else 1)


if __name__ == "__main__":
    main()
