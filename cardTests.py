import datetime
import functools
import operator
import random
import unittest
import genetic

class Fitness:
    def __init__(self, group1Sum, group2Product, duplicateCount):
        self.Group1Sum = group1Sum
        self.Group2Product = group2Product
        sumDifference = abs(36 - group1Sum)
        productDifference = abs(360 - group2Product)
        self.TotalDifference = sumDifference + productDifference
        self.DuplicateCount = duplicateCount

    def __gt__(self, other):
        if self.DuplicateCount != other.DuplicateCount:
            return self.DuplicateCount < other.DuplicateCount
        return self.TotalDifference < other.TotalDifference

    def __str__(self):
        return "sum: {} prod: {} dups: {}".format(self.Group1Sum, self.Group2Product, self.DuplicateCount)

def mutate(genes, geneset):
    if len(genes) == len(set(genes)):
        count = random.randint(1, 4)
        while count > 0:
            count -= 1
            indexA, indexB = random.sample(range(len(genes)), 2)
            genes[indexA], genes[indexB] = genes[indexB], genes[indexA]
    else:
        indexA = random.randrange(0, len(genes))
        indexB = random.randrange(0, len(geneset))
        genes[indexA] = geneset[indexB]

def get_fitness(genes):
    group1Sum = sum(genes[0:5])
    group2Product = functools.reduce(operator.mul, genes[5:10])
    duplicateCount = (len(genes) - len(set(genes)))
    return Fitness(group1Sum, group2Product, duplicateCount)

def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    sumGroup = ', '.join(map(str, candidate.Genes[0:5]))
    productGroup = ', '.join(map(str, candidate.Genes[5:10]))
    print("{} – {}\t{}\t{}".format(sumGroup, productGroup, candidate.Fitness, timeDiff))

class CardTests(unittest.TestCase):
    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test())

    def test(self):
        geneset = [i + 1 for i in range(10)]
        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnMutate(genes):
            mutate(genes, geneset)

        def fnGetFitness(genes):
            return get_fitness(genes)

        optimalFitness = Fitness(36, 360, 0)
        best = genetic.get_best(fnGetFitness, 10, optimalFitness, geneset, fnDisplay, fnMutate)
        self.assertTrue(not optimalFitness > best.Fitness)

if __name__ == '__main__':
    unittest.main()
