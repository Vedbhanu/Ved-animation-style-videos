"""Background score: playful bed whose mood follows the script sections.
usage (run automatically by render.py): score.py <out.wav> <engine_dir>
Edit SECTIONS: (start_line_index, chords, drum_style, extra kwargs). Moods: bright = F C G C / C G Am F,
tense = Am Em F E / Am F C E, sad = Dm Am (bell, no drums), building = C F G G with step=0.25."""
import json, os, sys

out, engine = sys.argv[1], sys.argv[2]
sys.path.insert(0, engine)
from music_lib import Score, CH  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LINES = json.load(open(os.path.join(HERE, "..", "build", "lines.json")))
L = [l["start"] for l in LINES]
END = LINES[-1]["end"] + 1.5

s = Score(END, seed=21)
BPM = 104
BEAT = 60 / BPM
BAR = 4 * BEAT


def section(t0, t1, prog, style=None, arp=0.04, drum=0.18, bass=0.06, step=0.5, inst="pluck", pad=0.0):
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


# (first line index, chords, drum style, kwargs) -- one row per mood change in the script
SECTIONS = [
    (0, ["C", "G", "Am", "F"], "pulse", dict(drum=0.16)),
    # (3, ["Am", "Em", "F", "E"], "half", dict(pad=0.025)),
    # (6, ["Dm", "Am"], None, dict(inst="bell", step=1, pad=0.03)),
]
for k, (li, prog, style, kw) in enumerate(SECTIONS):
    t0 = L[li]
    t1 = L[SECTIONS[k + 1][0]] if k + 1 < len(SECTIONS) else END
    section(t0, t1, prog, style, **kw)
s.render(out, wet=0.3, room=2.0)
