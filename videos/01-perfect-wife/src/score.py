"""Background score: playful pizzicato bed whose mood follows the script sections.
usage: score.py <out.wav> <engine_dir>"""
import json, os, sys

out, engine = sys.argv[1], sys.argv[2]
sys.path.insert(0, engine)
from music_lib import Score, CH  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
L = [l["start"] for l in json.load(open(os.path.join(HERE, "..", "build", "lines.json")))]
END = json.load(open(os.path.join(HERE, "..", "build", "lines.json")))[-1]["end"] + 1.5

s = Score(END, seed=21)
BPM = 104
BEAT = 60 / BPM
BAR = 4 * BEAT


def section(t0, t1, prog, style=None, arp=0.04, drum=0.2, bass=0.06, step=0.5, inst="pluck", pad=0.0):
    t, i = t0, 0
    while t < t1 - 0.05:
        notes, b = CH[prog[i % len(prog)]]
        d = min(BAR, t1 - t)
        s.arp(notes, t, d, BEAT * step, amp=arp, inst=inst)
        if bass:
            s.bass(b, t, d * 0.9, amp=bass)
        if pad:
            s.pad(notes, t, d + 0.3, amp=pad)
        t += BAR
        i += 1
    if style:
        s.drum_loop(t0, t1 - t0, BPM, amp=drum, style=style)


section(0.0, L[2], ["C", "G", "Am", "F"], "pulse", drum=0.16)                    # hook
section(L[2], L[3], ["F", "C", "G", "C"], "rock", drum=0.16, arp=0.045)          # good wife: bright
section(L[3], L[4], ["Am", "Em", "F", "E"], "half", drum=0.2, pad=0.025)         # bad wife: tense
section(L[4], L[8], ["C", "Am", "F", "G"], "pulse", drum=0.14)                   # ideals
section(L[8], L[10], ["C", "F", "G", "G"], "rock", drum=0.22, step=0.25, arp=0.035)  # AND list: building
section(L[10], L[11], ["Dm", "Am"], None, arp=0.03, inst="bell", step=1, pad=0.03)   # zero chance: sad
section(L[11], L[13], ["F", "C", "G", "C"], "pulse", drum=0.14)                  # options / docile wife
section(L[13], L[18], ["Am", "F", "C", "E"], "half", drum=0.17, pad=0.02)        # what you can never have
section(L[18], END, ["F", "G", "C", "C"], "rock", drum=0.16, arp=0.045, pad=0.02)  # resolution + outro
s.render(out, wet=0.3, room=2.0)
