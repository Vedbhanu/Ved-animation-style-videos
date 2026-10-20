"""Draw every Nth frame (no encode) and report any that raise. usage: PY scan_frames.py <project> [step=1]"""
import os, sys, traceback
SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SK, "engine"))
import render  # noqa: E402
m = render.load(os.path.abspath(sys.argv[1]))
step = int(sys.argv[2]) if len(sys.argv) > 2 else 1
bad = []
for f in range(0, int(m.DURATION * 30), step):
    try:
        render.draw(m, f / 30, wobble=False)
    except Exception:
        if not bad:
            traceback.print_exc()
        bad.append(round(f / 30, 2))
print("bad frames:", bad[:20], "..." if len(bad) > 20 else "")
sys.exit(1 if bad else 0)
