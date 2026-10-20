#!/bin/sh
# Word-level timestamps: build/voice.wav -> build/words.json  (whisper 'small')
# usage: words.sh <project_dir>
set -e
P="$1"
whisper "$P/build/voice.wav" --model small --language en --word_timestamps True --output_format json --output_dir "$P/build" >/dev/null 2>&1
python3 - "$P" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p + "/build/voice.json"))
w = [x for s in d["segments"] for x in s["words"]]
json.dump([{"w": x["word"].strip(), "s": round(x["start"], 2), "e": round(x["end"], 2)} for x in w],
          open(p + "/build/words.json", "w"))
L = json.load(open(p + "/build/lines.json"))
print(len(w), "words")
for l in L:
    ws = [x for x in w if l["start"] - 0.1 <= x["start"] < l["end"] + 0.2]
    print(f"\n[{l['i']}] {l['start']}-{l['end']}")
    print(" ".join(f"{x['word'].strip()}@{x['start']:.1f}" for x in ws))
PY
