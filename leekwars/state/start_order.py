import math


class StartOrder:
    """Handle the computation of entities starting order"""

    def __init__(self):
        self.teams = []
        self.totalEntities = 0

    def addEntity(self, entity) -> None:
        while len(self.teams) < entity.getTeam() + 1:
            self.teams.append([])
        self.teams[entity.getTeam()].append(entity)
        self.totalEntities += 1

    def compute(self, state):
        # Sort entities inside team on their frequency
        for team in self.teams:
            team.sort(key=lambda e: -e.getFrequency())

        # Compute probability for each team
        probas = []
        frequencies = []

        sum_ = 0
        for i in range(len(self.teams)):
            frequency = self.teams[i][0].getFrequency()
            frequencies.append(frequency)
            sum_ += frequency

        psum = 0.0
        for i in range(len(self.teams)):
            f = float(frequencies[i])
            p = 1.0 / (1.0 + math.pow(10, (sum_ - f) / 100.0))
            probas.append(p)
            psum += p

        for i in range(len(self.teams)):
            probas[i] = probas[i] / psum
        psum = 1

        # Compute team order
        teamOrder = []
        remaining = []
        for i in range(len(self.teams)):
            remaining.append(i)

        for t in range(len(self.teams)):
            v = state.getRandom().get_double()

            for i in range(len(remaining)):
                team = remaining[i]
                p = probas[team]

                if v <= p:
                    teamOrder.append(team)
                    remaining.pop(i)
                    psum -= p
                    break
                v -= p

            for i in range(len(self.teams)):
                # Match Java double / 0 → Inf semantics (not an exception)
                probas[i] = float('inf') if psum == 0 else probas[i] / psum
            psum = 1

        # Compute entity order
        order = []
        currentTeamI = 0
        while len(order) != self.totalEntities:
            team = teamOrder[currentTeamI]
            if len(self.teams[team]) > 0:
                order.append(self.teams[team].pop(0))
            currentTeamI = (currentTeamI + 1) % len(self.teams)

        return order
