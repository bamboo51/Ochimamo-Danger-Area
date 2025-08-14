import numpy as np
import random

NUM_BEACONS = 3
POPULATION_SIZE = 50
NUM_GENERATIONS = 100
MUTATION_RATE = 0.1
ELITISM_RATE = 0.1
SEED = 42

np.random.seed(SEED)
random.seed(SEED)

class GeneticAlgorithm:
    def __init__(self,
                 num_beacons=NUM_BEACONS,
                 population_size=POPULATION_SIZE,
                 num_generations=NUM_GENERATIONS,
                 mutation_rate=MUTATION_RATE,
                 elitism_rate=ELITISM_RATE,):
        self.num_beacons = num_beacons
        self.population_size = population_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.elitism_rate = elitism_rate

    def _create_individual(self, placement):
        """
        個体を生成する。各ビーコンの位置はランダムに決定される。
        """
        return random.sample(range(placement), self.num_beacons)
    
    def _calculate_fitness(self, individual, coverage_sets, centers, ble_px):
        """
        個体の適応度を計算する。カバレッジとビーコン間の距離を考慮する。
        """
        covered = set().union(*[coverage_sets[i] for i in individual])
        covered = len(covered) / len(centers)
        points = np.array([centers[i] for i in individual])
        if len(points) > 1:
            distances = np.linalg.norm(points[:, None, :] - points[None, :, :], axis=2)
            np.fill_diagonal(distances, np.inf)
            penalty = 0 if distances.min() >= ble_px / 4 else 0.5
        else:
            penalty = 0
        return covered - penalty
    
    def _crossover(self, parent1, parent2):
        """
        2つの親個体から子個体を生成する。ランダムに選択された遺伝子を組み合わせる。
        """
        g = list(set(parent1+parent2))
        random.shuffle(g)
        return g[:self.num_beacons]
    
    def _mutate(self, individual, placement):
        """
        個体に突然変異を適用する。ランダムに選択された遺伝子を変更する。
        """
        if random.random() < self.mutation_rate:
            individual[random.randrange(len(individual))] = random.randrange(placement)
        return individual
    
    def run(self, placement, center, coverage_set, ble_px):
        pop = [self._create_individual(len(placement)) for _ in range(self.population_size)]
        best_solution, best_fitness = None, -1

        for _ in range(self.num_generations):
            scored = [(self._calculate_fitness(individual, coverage_set, center, ble_px), individual) for individual in pop]
            scored.sort(reverse=True, key=lambda x: x[0])

            if scored[0][0] > best_fitness:
                best_fitness, best_solution = scored[0]

            elite_count = int(self.population_size * self.elitism_rate)
            elite = [individual for _, individual in scored[:elite_count]]
            new_population = elite[:]

            while len(new_population) < self.population_size:
                parent1, parent2 = random.choices(pop, k=2)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child, len(placement))
                new_population.append(child)

            pop = new_population

        return [placement[i] for i in best_solution]