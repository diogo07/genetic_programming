import operator
import math
import random
import matplotlib.pyplot as plt

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

'''
Configuração
Dupla 2
Tamanho da população        100
PC                          Variar
PM                          Variar
Funções                     +, -, x
'''

def protectedDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1


pset = gp.PrimitiveSet("MAIN", 1)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addEphemeralConstant("rand101", lambda: random.uniform(-1.0, 1.0))
pset.renameArguments(ARG0='x')

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


def evalSymbReg(individual, points):
    func = toolbox.compile(expr=individual)
    sqerrors = ((func(x) - math.pow(math.sin(x),2) + 0.8 * math.pow(math.cos(2*math.pi * x),2))**2 for x in points)
    return math.fsum(sqerrors) / len(points),


toolbox.register("evaluate", evalSymbReg, points=[x / 10. for x in range(-10, 10)])
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))


def main():
    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.5, 1000, stats=mstats,
                                   halloffame=hof, verbose=True)

    return pop, log, hof


def plot(original_function, candidate_function):
    x_values = [x / 10. for x in range(-10, 10)]

    print(x_values)

    original_points = []
    candidate_points = []

    for value in x_values:
        original_points.append(original_function(value))
        candidate_points.append(candidate_function(value))

    plt.plot(x_values, original_points, 'k', x_values, candidate_points, 'r')
    plt.show()


if __name__ == "__main__":
    results = main()

    expr = results[2][0]

    print(expr)

    tree = gp.PrimitiveTree(expr)

    candidate_function = toolbox.compile(tree)
    original_function = lambda x: math.sin(x) ** 2 - 0.8 * (math.cos(2*math.pi * x) ** 2)
    plot(original_function, candidate_function)
