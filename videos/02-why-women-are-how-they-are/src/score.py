"""Background score: playful pizzicato bed whose mood follows the script sections.
usage: score.py <out.wav> <engine_dir>"""
import json, os, sys

out, engine = sys.argv[1], sys.argv[2]
sys.path.insert(0, engine)
from music_lib import Score, CH  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
L = [l["start"] for l in json.load(open(os.path.join(HERE, "..", "build", "lines.json")))]
END = json.load(open(os.path.join(HERE, "..", "build", "lines.json")))[-1]["end"] + 1.5

s = Score(END, seed=42)
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


section(0.0, L[1], ["C", "G", "Am", "F"], "pulse", drum=0.15)                       # 0. hook: mistake / thinking like a man
section(L[1], L[3], ["Am", "Em", "F", "E"], "half", drum=0.18, pad=0.03)            # 1-2. pregnancy 70k cal & vulnerability
section(L[3], L[4], ["Am", "C", "G", "F"], "rock", drum=0.22, arp=0.045)           # 3. male competition
section(L[4], L[5], ["C", "G", "Am", "F"], "pulse", drum=0.14)                      # 4. survival software
section(L[5], L[6], ["Am", "F", "C", "G"], "half", drum=0.16, pad=0.02)            # 5. dominance & submission
section(L[6], L[7], ["C", "Am", "F", "G"], "pulse", drum=0.15)                      # 6. hypergamy
section(L[7], L[8], ["F", "C", "G", "C"], "rock", drum=0.18, arp=0.045)            # 7. king vs queen contrast
section(L[8], L[9], ["C", "G", "Am", "F"], "pulse", drum=0.15)                      # 8. resource stability over looks
section(L[9], L[10], ["Am", "Em", "F", "G"], "pulse", drum=0.16, pad=0.02)         # 9. emotional attunement / how you said it
section(L[10], L[11], ["Dm", "Am", "G", "C"], "half", drum=0.17, pad=0.025)        # 10. bell curve variance
section(L[11], L[12], ["Am", "Em", "F", "E"], "half", drum=0.18, pad=0.02)         # 11. stop getting bitter
section(L[12], L[13], ["F", "G", "C", "C"], "rock", drum=0.18, arp=0.05, pad=0.02) # 12. eyes wide open: resolution
section(L[13], END, ["C", "F", "G", "C"], "rock", drum=0.20, arp=0.05, pad=0.02)   # 13-14. book CTA + part 3
s.render(out, wet=0.3, room=2.0)
