"""Narration: <project>/script.md -> build/voice.wav + build/lines.json  (Kokoro, voice am_puck).

usage: TTS_PY tts.py <project_dir> [--voice am_puck] [--speed 1.12]
script.md format: optional header, a line with only '---', then one paragraph per beat (blank-line separated).
Each paragraph becomes one 'line' (LINES[i] in scenes.py) with exact start/end times.
"""
import sys, os, re, json, argparse
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

ap = argparse.ArgumentParser()
ap.add_argument("proj")
ap.add_argument("--voice", default="am_puck")
ap.add_argument("--speed", type=float, default=1.12)
ap.add_argument("--gap", type=float, default=0.35)
a = ap.parse_args()
proj = a.proj
d = os.path.expanduser("~/.cache/animated-short/tts/")
k = Kokoro(d + "kokoro-v1.0.onnx", d + "voices-v1.0.bin")
raw = open(os.path.join(proj, "script.md")).read()
raw = raw.split("\n---", 1)[1] if "\n---" in raw else raw
paras = [p.strip() for p in raw.split("\n\n") if p.strip() and not p.strip().startswith("#")]


def speakable(t):
    t = re.sub(r"(\d+(?:\.\d+)?)%", lambda m: m.group(1) + " percent", t)
    t = t.replace("…", "...").replace("IQ", "I.Q.")
    # Kokoro spells out ALL-CAPS words; lowercase them (keeps 'I')
    return re.sub(r"\b[A-Z]{2,}\b", lambda m: m.group(0).lower(), t)


SR = 24000
out, lines, t = [], [], 0.0
os.makedirs(os.path.join(proj, "build"), exist_ok=True)
for i, p in enumerate(paras):
    audio, sr = k.create(speakable(p), voice=a.voice, speed=a.speed, lang="en-us")
    gap = a.gap if i < len(paras) - 1 else 0.8
    lines.append({"i": i, "text": p, "start": round(t, 3), "end": round(t + len(audio) / SR, 3)})
    out += [audio, np.zeros(int(gap * SR), dtype=audio.dtype)]
    t += len(audio) / SR + gap
sf.write(os.path.join(proj, "build", "voice.wav"), np.concatenate(out), SR)
json.dump(lines, open(os.path.join(proj, "build", "lines.json"), "w"), indent=1)
words = sum(len(p.split()) for p in paras)
print(f"{len(paras)} paragraphs, {words} words, {t:.1f}s ({words / t * 60:.0f} wpm)")
