#!/bin/sh
# Idempotent environment check/setup for the Chaaya video skill.
# Prints two lines at the end:  PY=<render python>   TTS_PY=<kokoro python>
# Render env (pycairo + numpy) and Kokoro TTS live in ~/.cache/animated-short (shared with older skills).
set -e
CACHE="$HOME/.cache/animated-short"
PY="$CACHE/venv/bin/python"
TTS="$CACHE/tts"
TTS_PY="$TTS/venv/bin/python"
command -v ffmpeg >/dev/null || { echo "ffmpeg missing: brew install ffmpeg" >&2; exit 1; }
command -v whisper >/dev/null || echo "WARNING: whisper CLI missing (pip install openai-whisper) - needed for word timings" >&2

# 1. render env
if ! { [ -x "$PY" ] && "$PY" -c "import cairo, numpy" 2>/dev/null; }; then
  if [ -x "$HOME/.claude/skills/animated-short/scripts/setup.sh" ]; then
    "$HOME/.claude/skills/animated-short/scripts/setup.sh" >/dev/null
  else
    BREW=$(brew --prefix 2>/dev/null || echo /opt/homebrew)
    [ -f "$BREW/lib/pkgconfig/cairo.pc" ] || brew install cairo
    python3 -m venv "$CACHE/venv"
    "$CACHE/venv/bin/pip" install -q --upgrade pip numpy pycairo
  fi
fi
"$PY" -c "import cairo, numpy" || { echo "render env broken" >&2; exit 1; }

# 2. Kokoro TTS (voice am_puck)
mkdir -p "$TTS"
if ! { [ -x "$TTS_PY" ] && "$TTS_PY" -c "import kokoro_onnx, soundfile" 2>/dev/null; }; then
  python3 -m venv "$TTS/venv"
  "$TTS/venv/bin/pip" install -q --upgrade pip kokoro-onnx soundfile
fi
BASE="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
[ -f "$TTS/kokoro-v1.0.onnx" ] || curl -L -o "$TTS/kokoro-v1.0.onnx" "$BASE/kokoro-v1.0.onnx"
[ -f "$TTS/voices-v1.0.bin" ] || curl -L -o "$TTS/voices-v1.0.bin" "$BASE/voices-v1.0.bin"
echo "PY=$PY"
echo "TTS_PY=$TTS_PY"
