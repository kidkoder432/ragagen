from heapq import nlargest
import numpy as np
import json
from pprint import pprint

from sympy import S
from genetic_algo import fitness, cross_over, mutate, swar2int
from midiutil import MIDIFile as MidiFile


SWARS = "'S 'r 'R 'g 'G 'M 'm 'P 'd 'D 'n 'N S r R g G M m P d D n N S' r' R' g' G' M' m' P' d' D' n' N'".split()

epsilon = 0.5

POPULATION_LEN = 20

tpm = np.load("tpm.npy")


def getfromtpm(tpm, note, temp=1.0):

    r = tpm[SWARS.index(note)]

    if sum(r) == 0:  # NaN -> no pairs, try finding a note in a different octave
        return note
    r = r ** (1.0 / temp)
    r = r / sum(r)
    for i in range(len(r)):
        if r[i] == np.NaN:
            r[i] = 0
    return np.random.choice(SWARS, p=r)


def flatten(xss):
    return [x for xs in xss for x in xs]


raga = json.load(open("durga.json", encoding="utf-8"))

aaroh = raga["aaroh"].split(" ")

allowed_swar = sorted(
    flatten([[x, "'" + x, x + "'"] for x in aaroh[:-1]]), key=lambda x: SWARS.index(x)
)

chromosomes = []

for i in range(50):
    chromosomes.append([])
    startNote = "'D"
    for j in range(POPULATION_LEN):
        if np.random.random() < epsilon:  # Exploit
            nextNote = getfromtpm(tpm, startNote)
        else:  # Explore
            nextNote = np.random.choice(allowed_swar)
        chromosomes[-1].append(nextNote)
        startNote = nextNote

population = {" ".join(x): fitness(x) for x in chromosomes}

pprint(population.values())

overallFitness = sum(population.values()) / len(population)
prevOverallFitness = 0

gen = 1
while overallFitness < 90 and gen < 400:
    print("Generation", gen)

    d = [x / sum(population.values()) for x in population.values()]
    d = np.array(d)
    gen += 1
    best_parents = np.random.choice(
        list(population.keys()),
        size=12,
        p=d,
    )

    best_parents = nlargest(12, population, key=population.get)
    # for i in best_parents:
    #     print(i[:10], fitness(i.split(" ")))

    population = {i: fitness(i.split(" ")) for i in best_parents}

    passes = 0
    while len(population) < 50 and passes < 400:
        passes += 1
        p1 = np.random.choice(best_parents).split(" ")
        p2 = np.random.choice(best_parents).split(" ")
        do_crossover = np.random.random() < 0.5
        do_mutation = np.random.random() < 0.1

        res1, res2 = None, None
        if do_crossover:
            for i in range(POPULATION_LEN):
                k = np.random.randint(0, len(p1))
                res1, res2 = cross_over(p1, p2, k)
                if res1 is not None:
                    break

        elif do_mutation:
            pass
            res1 = mutate(p1)

        else:
            continue

        if res1 is not None:
            res1 = " ".join(res1)
            if res1 in population:
                continue
            population[res1] = fitness(res1.split(" "))

        if res2 is not None:
            res2 = " ".join(res2)
            if res2 in population:
                continue
            population[res2] = fitness(res2.split(" "))

    prevOverallFitness = overallFitness
    overallFitness = sum(population.values()) / len(population)
    print("Overall fitness", overallFitness)

print(population.values())

tonic = 56


def makeMidi(sample):
    mid = MidiFile()
    mid.addTrackName(0, 0, "Sample")
    mid.addTempo(0, 0, 160)
    v = 100
    b = 0
    for s in sample.split(" "):
        mid.addNote(0, 0, swar2int(s) + tonic - 12, b, 0.9, v)
        b += 1
    with open("output.mid", "wb") as output_file:
        mid.writeFile(output_file)


s = max(population, key=population.get)

print(s, population[s])
makeMidi(s)
