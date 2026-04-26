"""Run a single battle with a Python AI.

Usage:
    python run_battle.py [seed]

If no seed is supplied, a random one is generated.
"""

import json
import sys
import random

from leekwars.generator import Generator
from leekwars.scenario.scenario import Scenario
from leekwars.scenario.farmer_info import FarmerInfo
from leekwars.scenario.team_info import TeamInfo
from leekwars.scenario.entity_info import EntityInfo
from leekwars.statistics.statistics_manager import DefaultStatisticsManager
from leekwars.fight.statistics_manager import StatisticsManager as FightStatisticsManager
from leekwars.leek.register_manager import RegisterManager
from example_ai import basic_ai


class FightStats(DefaultStatisticsManager):
    """A no-op statistics manager that satisfies the fight-aware interface."""

    def setGeneratorFight(self, fight):
        self._fight = fight


class NoopRegisterManager(RegisterManager):

    def getRegisters(self, leek):
        return None

    def saveRegisters(self, leek, registers, is_new):
        pass


def make_random_scenario(seed: int) -> Scenario:
    rng = random.Random(seed)
    scenario = Scenario()
    scenario.seed = seed
    scenario.maxTurns = 64
    scenario.type = 0  # solo
    scenario.context = 0  # test

    # Two farmers, two teams
    f1 = FarmerInfo(); f1.id = 1; f1.name = "Player1"; f1.country = "fr"
    f2 = FarmerInfo(); f2.id = 2; f2.name = "Player2"; f2.country = "fr"
    scenario.farmers[1] = f1
    scenario.farmers[2] = f2

    t1 = TeamInfo(); t1.id = 1; t1.name = "TeamA"
    t2 = TeamInfo(); t2.id = 2; t2.name = "TeamB"
    scenario.teams[1] = t1
    scenario.teams[2] = t2

    # Two random entities
    for team_id, farmer_id, name, ai in [(1, 1, "Fighter1", basic_ai), (2, 2, "Fighter2", basic_ai)]:
        e = EntityInfo()
        e.id = team_id * 10
        e.name = name
        e.type = 0  # leek
        e.farmer = farmer_id
        e.team = team_id
        e.level = rng.randint(50, 200)
        e.life = rng.randint(2000, 5000)
        e.strength = rng.randint(100, 400)
        e.agility = rng.randint(0, 200)
        e.wisdom = rng.randint(0, 200)
        e.resistance = rng.randint(0, 200)
        e.science = rng.randint(0, 200)
        e.magic = rng.randint(0, 200)
        e.frequency = rng.randint(0, 100)
        e.tp = rng.randint(8, 20)
        e.mp = rng.randint(4, 10)
        e.cores = 10
        e.ram = 10
        e.weapons = [37]  # PISTOL
        e.chips = []
        e.ai_function = ai
        scenario.addEntity(team_id - 1, e)

    return scenario


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(1, 2 ** 30)
    print(f"Running battle with seed={seed}")

    generator = Generator(data_dir="data")
    scenario = make_random_scenario(seed)
    stats = FightStats()
    register_manager = NoopRegisterManager()

    outcome = generator.runScenario(scenario, None, register_manager, stats)

    print(f"Winner team: {outcome.winner}")
    print(f"Duration: {outcome.duration} turns")
    if outcome.exception is not None:
        print(f"Exception: {outcome.exception}")

    # Dump fight JSON for comparison
    if outcome.fight is not None:
        out = outcome.fight.toJSON()
        with open(f"out_python_{seed}.json", "w", encoding="utf-8") as f:
            json.dump(out, f, default=str, sort_keys=True)
        print(f"Wrote out_python_{seed}.json")


if __name__ == "__main__":
    main()
