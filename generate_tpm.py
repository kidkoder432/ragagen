import numpy as np
import json


SWARS = "'S 'r 'R 'g 'G 'M 'm 'P 'd 'D 'n 'N S r R g G M m P d D n N S' r' R' g' G' M' m' P' d' D' n' N'".split()

tpm = np.zeros((len(SWARS), len(SWARS)))

raga = json.load(open("durga.json", encoding="utf-8"))

NOTES = raga["raga_data"]

important_notes = ["S", "'S", "S'"]

v = raga["vadi"]
important_notes += [v, "'" + v, v + "'"]

sv = raga["samvadi"]
important_notes += [sv, "'" + sv, sv + "'"]

important_notes = list(set(important_notes))

phrase = NOTES.split(" ")

for i in range(len(phrase) - 1):
    print(phrase[i], end=" ")
    tpm[SWARS.index(phrase[i]), SWARS.index(phrase[i + 1])] += 1.0


print(np.sum(tpm), len(NOTES))
for i in range(len(SWARS)):
    if np.sum(tpm[i]) > 0:
        tpm[i] /= np.sum(tpm[i])

for i in important_notes:
    tpm[SWARS.index(i)] *= 1.2
    tpm.T[SWARS.index(i)] *= 1.2

print(tpm)
np.save("tpm.npy", tpm)
