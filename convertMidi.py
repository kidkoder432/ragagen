from turtle import end_fill
from librosa import ex
import mido

import json

mid = mido.MidiFile("./Durga (1).mid")

notes = {}

tonic = 56

messages = mid.tracks[0]

notes = [0]

for msg in messages:
    if msg.type == "note_on":
        notes.append(msg.note - 12)
        print(msg.note, end=" ")
    else:
        print(msg)

print(len(notes))

swars = {
    tonic - 12: "'S",
    tonic - 11: "'r",
    tonic - 10: "'R",
    tonic - 9: "'g",
    tonic - 8: "'G",
    tonic - 7: "'M",
    tonic - 6: "'m",
    tonic - 5: "'P",
    tonic - 4: "'d",
    tonic - 3: "'D",
    tonic - 2: "'n",
    tonic - 1: "'N",
    tonic: "S",
    tonic + 1: "r",
    tonic + 2: "R",
    tonic + 3: "g",
    tonic + 4: "G",
    tonic + 5: "M",
    tonic + 6: "m",
    tonic + 7: "P",
    tonic + 8: "d",
    tonic + 9: "D",
    tonic + 10: "n",
    tonic + 11: "N",
    tonic + 12: "S'",
    tonic + 13: "r'",
    tonic + 14: "R'",
    tonic + 15: "g'",
    tonic + 16: "G'",
    tonic + 17: "M'",
    tonic + 18: "m'",
    tonic + 19: "P'",
    tonic + 20: "d'",
    tonic + 21: "D'",
    tonic + 22: "n'",
    tonic + 23: "N'",
}

d = json.load(open("durga.json", encoding="utf-8"))
d["raga_data"] = " ".join([swars.get(i, "") for i in notes])

json.dump(d, open("durga.json", "w"))
