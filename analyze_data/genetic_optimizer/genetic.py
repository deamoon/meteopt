from random import random
from random import randrange
import threading

class GeneticOptimizer:

    class CalculatingThread(threading.Thread):
        def __init__(self, results, population, algorithm, start_index, step):
            threading.Thread.__init__(self)
            self.start_index = start_index
            self.algorithm = algorithm
            self.results = results
            self.step = step
            self.population = population
        
        def run(self):
            size = len(self.results)
            for i in range(self.start_index, size, self.step):
                self.results[i] = self.algorithm(*self.population[i])
        
    def __init__(self, popsize, algorithm, arglow, arghigh, argdiscrete, mutation_chance = 0.01, num_of_threads = 4):
        self.algorithm = algorithm
        self.arglow = arglow
        self.arghigh = arghigh
        self.argcount = len(arglow)
        self.argdiscrete = argdiscrete
        self.popsize = popsize
        self.mutation_chance = mutation_chance
        self.num_of_threads = num_of_threads
        
    def generate_new_argument_value(self, index):
        if (self.argdiscrete[index]):
            return randrange(self.arglow[index], self.arghigh[index] + 1)
        else:
            return random() * (self.arghigh[index] - self.arglow[index]) + self.arglow[index] 
    
    def create_population(self):
        self.population = [[0] * self.argcount for i in range(self.popsize)]
        for gene in self.population:
            for i in range(0, self.argcount):
                gene[i] = self.generate_new_argument_value(i)
    
    def calculate_results(self):
        self.results = [0] * self.popsize
        threads = [self.CalculatingThread(self.results, self.population, self.algorithm, i, self.num_of_threads) for i in range(0, self.num_of_threads)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
    def count_survivability(self):
        self.calculate_results()
        for i in range(self.popsize):
            self.results[i] = pow(self.results[i], 2)
        self.percentage_range = [0] * self.popsize
        sum = 0
        for i in range(self.popsize):
            sum += self.results[i]
        for i in range(self.popsize):
            self.percentage_range[i] = self.results[i] / sum
        for i in range(1, self.popsize):
            self.percentage_range[i] += self.percentage_range[i - 1]
            
    def get_random_gene(self):
        r = random()
        for i in range(self.popsize):
            if r <= self.percentage_range[i]:
                return self.population[i]
            
    def create_new_population(self):
        new_population = [[0] * self.argcount for i in range(self.popsize)]
        for i in range(self.popsize):
            father = self.get_random_gene()
            mother = self.get_random_gene()
            for j in range(self.argcount):
                if random() > 0.5:
                    new_population[i][j] = father[j]
                else:
                    new_population[i][j] = mother[j]
        self.population = new_population
        
    def mutate(self):
        for gene in self.population:
            for i in range(self.argcount):
                if random() <= self.mutation_chance:
                    gene[i] = self.generate_new_argument_value(i)
                
      
    def run(self, generations):
        self.create_population()
        for generation in range(generations):
            self.count_survivability()
            self.create_new_population()
            if generation == generations - 1:
                self.mutate()
        self.calculate_results()
        
def show(v):
    a.run(v)
    print('\n'.join([str(x) for x in a.population]))
    print('\n'.join([str(x) for x in a.results]))
        
a = GeneticOptimizer(100, lambda a, b, c, d: a + b + c + d, [0, 0, 0, 0], [1, 5, 10, 1], [True, True, True, True], 0.01)
show(1)
