import json

import numpy as np

# Implementation of "Markov-based genetic algorithm with 𝜖-greedy exploration
# for Indian classical music composition" (https://doi.org/10.1016/j.eswa.2022.118561)

raga = json.load(open("durga.json", encoding="utf-8"))

SWARS = "'S 'r 'R 'g 'G 'M 'm 'P 'd 'D 'n 'N S r R g G M m P d D n N S' r' R' g' G' M' m' P' d' D' n' N'".split()

pakad = raga["pakad"]


def flatten(xss):
    return [x for xs in xss for x in xs]


def swar2int(s):
    return SWARS.index(s)


aaroh = raga["aaroh"].split(" ")

allowed_aaroh = sorted(
    flatten([[x, "'" + x, x + "'"] for x in aaroh[:-1]]), key=swar2int
)

allowed_avroh = reversed(allowed_aaroh)

weights = {
    "aa": 3,  # Adhere to Aaroh and Avaroh
    "ol": 5,  # Obnoxious Leaps
    "lr": 2,  # Leap Resolution
    "or": 2,  # Octave Range
    "npr": 3,  # Note Repetition
}


def to_str(seq):
    return " ".join(seq)


def random_frag(s):
    a = np.random.randint(0, len(s) - 5)
    b = np.random.randint(a + 3, len(s))

    return s[a:b]


# Fitness function for evaluating generated raga phrases
def fitness(seq):

    # Adhere to Aaroh and Avaroh (AA)
    # This function counts the number of notes that do not follow aaroh and avroh.

    count = 0
    for i in range(len(seq) - 1):
        if to_str(seq[i : i + 2]) not in to_str(allowed_aaroh) and to_str(
            seq[i : 1 + 2]
        ) not in to_str(allowed_avroh):
            count += 1

    fitness_aa = weights["aa"] * count

    # Obnoxious Leaps (OL)
    # This function counts the number of leaps (jumps) greater than 6 notes.

    count = 0
    for i in range(len(seq) - 1):
        if abs(swar2int(seq[i + 1]) - swar2int(seq[i])) > 6:
            count += 1

    fitness_ol = weights["ol"] * count

    # Leap Resolution (LR)
    # Counts the number of large leaps that do not resolve.
    # A leap is resolved when the next note after the leap
    # occurs in the opposite direction.

    count = 0
    for i in range(len(seq) - 2):
        diff = swar2int(seq[i + 1]) - swar2int(seq[i])
        leap_dist = abs(diff)
        leap_dir = np.sign(diff)

        next_diff = swar2int(seq[i + 2]) - swar2int(seq[i + 1])
        next_dir = np.sign(next_diff)

        if leap_dir != -next_dir and leap_dist > 8:
            count += 1

    fitness_lr = weights["lr"] * count

    # Octave Range (OR)
    # Gives a penalty if the octave range of the sequence
    # is greater than 2 octaves.

    minNote = min([swar2int(x) for x in seq])
    maxNote = max([swar2int(x) for x in seq])

    if maxNote - minNote > 24:
        fitness_or = weights["or"] * 4
    else:
        fitness_or = weights["or"] * 0

    # Note and Phrase Repetition (NPR)
    # This function counts the number of
    # consecutive occurrences of the same note or phrase
    # within the sequence.

    count = 0
    for j in range(1, 6):
        for i in range(2 * j, len(seq)):
            if seq[i - 2 * j : i - j] == seq[i - j : i]:
                count += 1

    fitness_npr = weights["npr"] * count

    return 150 - (fitness_aa + fitness_ol + fitness_lr + fitness_or + fitness_npr) / 5


def cross_over(parent1, parent2, k):
    # Crossover
    # Randomly selects an eligible point in the sequence to cross
    # two parent sequences

    child1 = parent1[:k] + parent2[k:]
    child2 = parent2[:k] + parent1[k:]

    # Eligibility check
    # 0. Repetition -> ok (will be weeded out in fitness)
    if parent1[k] == parent2[k]:
        return child1, child2

    # 1. Aaroh-Avroh Consistency
    cross = parent1[k] + parent2[k]
    if to_str(cross) not in to_str(allowed_aaroh) and to_str(cross) not in to_str(
        allowed_avroh
    ):
        return None, None  # Breaks AA

    # 2. Large Leaps
    if abs(swar2int(parent1[k]) - swar2int(parent2[k])) > 12:
        return None, None  # Breaks OL

    return child1, child2


def mutate(seq):
    # Mutation
    # Randomly mutates a parent sequence by inserting a
    # fragment of Pakad at a random location
    # (Some locations will be ineligible;
    # these will be weeded out in fitness)

    frag = random_frag(pakad.split(" "))
    k = np.random.randint(len(frag), len(seq) - len(frag))

    return seq[:k] + frag + seq[k + len(frag) :]

