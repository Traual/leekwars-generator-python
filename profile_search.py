"""Profile the BFS-dim-1 hot path to find what's left to squeeze."""
import cProfile, pstats, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leekwars.effect
from leekwars.state.state import State
from leekwars.weapons import weapons as Weapons
from bench_search import setup_state

_, state = setup_state(seed=42)
cur = state.getOrder().current()
weapon = Weapons.getWeapon(cur.getWeapons()[0].getId())
enemies = [e for e in state.getEntities().values() if e.getTeam() != cur.getTeam() and e.isAlive()]
target_cell = enemies[0].getCell()


def run(n):
    for _ in range(n):
        c = State(state)
        cur2 = c.getOrder().current()
        c.setWeapon(cur2, weapon)
        c.useWeapon(cur2, target_cell)
        for e in c.getEntities().values():
            _ = (e.getLife(), e.getCell())


pr = cProfile.Profile()
pr.enable()
run(5000)
pr.disable()
s = io.StringIO()
pstats.Stats(pr, stream=s).strip_dirs().sort_stats('tottime').print_stats(20)
print(s.getvalue())
