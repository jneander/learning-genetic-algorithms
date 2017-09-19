from bisect import bisect_left
from math import exp
import random
import statistics
import sys
import time

class Benchmark:
    @staticmethod
    def run(function):
        timings = []
        stdout = sys.stdout
        for i in range(100):
            sys.stdout = None
            startTime = time.time()
            function()
            seconds = time.time() - startTime
            sys.stdout = stdout
            timings.append(seconds)
            mean = statistics.mean(timings)
            report = "\r{} {:3.2f} {:3.2f}".format(1 + i, mean, statistics.stdev(timings, mean) if i > 1 else 0)
            sys.stdout.write(report)
            sys.stdout.flush()
        print()

class Chromosome:
    def __init__(self, genes, fitness):
        self.Genes = genes
        self.Fitness = fitness
        self.Age = 0

def _mutate(parent, geneSet, get_fitness):
    childGenes = parent.Genes[:]
    index = random.randrange(0, len(parent.Genes))
    newGene, alternate = random.sample(geneSet, 2) # get two, in case the first matches
    childGenes[index] = alternate if newGene == childGenes[index] else newGene
    fitness = get_fitness(childGenes)
    return Chromosome(childGenes, fitness)

def _mutate_custom(parent, custom_mutate, get_fitness):
    childGenes = parent.Genes[:]
    custom_mutate(childGenes)
    fitness = get_fitness(childGenes)
    return Chromosome(childGenes, fitness)

def _generate_parent(length, geneSet, get_fitness):
    genes = []
    while len(genes) < length:
        sampleSize = min(length - len(genes), len(geneSet))
        genes.extend(random.sample(geneSet, sampleSize))
    fitness = get_fitness(genes)
    return Chromosome(genes, fitness)

def _get_improvement(new_child, generate_parent, maxAge):
    parent = bestParent = generate_parent()
    yield bestParent
    historicalFitnesses = [bestParent.Fitness]
    while True:
        child = new_child(parent)
        if parent.Fitness > child.Fitness:
            if maxAge is None:
                continue # we got worse and are not pursuing lineage; move on to the next iteration
            parent.Age += 1
            if maxAge > parent.Age:
                continue # we got worse, but have another chance; move on to the next iteration
            index = bisect_left(historicalFitnesses, child.Fitness, 0, len(historicalFitnesses))
            difference = len(historicalFitnesses) - index
            proportionSimilar = difference / len(historicalFitnesses)
            if random.random() < exp(-proportionSimilar): # the child was far from the best fitness
                parent = child
                continue
            parent = bestParent
            parent.Age = 0
            continue
        if not child.Fitness > bestParent.Fitness:
            child.Age = parent.Age + 1
            parent = child
            continue # not better, but swap in case it helps progress
        parent = child
        parent.Age = 0
        if child.Fitness > bestParent.Fitness:
            yield child
            bestParent = child
            historicalFitnesses.append(child.Fitness)

def get_best(
        get_fitness, targetLen, optimalFitness, geneSet, display, custom_mutate=None, custom_create=None, maxAge=0
        ):
    random.seed()

    if custom_mutate is None:
        def fnMutate(parent):
            return _mutate(parent, geneSet, get_fitness)
    else:
        def fnMutate(parent):
            return _mutate_custom(parent, custom_mutate, get_fitness)

    if custom_create is None:
        def fnGenerateParent():
            return _generate_parent(targetLen, geneSet, get_fitness)
    else:
        def fnGenerateParent():
            genes = custom_create()
            return Chromosome(genes, get_fitness(genes))

    for improvement in _get_improvement(fnMutate, fnGenerateParent, maxAge):
        display(improvement)
        if not optimalFitness > improvement.Fitness:
            return improvement
