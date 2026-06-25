class GroverEngine:
    def __init__(self, gower, consensus, objective):
        self.gower = gower
        self.consensus = consensus
        self.objective = objective

    def step(self, hypotheses, observations):
        # 1. Геометрия
        sim_matrix = self.gower.compute(hypotheses, observations)

        # 2. Локальное обновление весов
        weights = self.probabilistic_update(sim_matrix)

        # 3. Grover Amplification (усиление разрыва)
        amplified = self.amplify(weights, temperature=1.5)

        # 4. Gossip с соседями
        self.consensus.gossip(amplified)

        # 5. Проверка сходимости
        if self.objective.is_converged(amplified):
            return self.extract_best(amplified)
        return None
