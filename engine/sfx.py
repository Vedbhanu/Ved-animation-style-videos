"""Synthesized cartoon sound effects, mixed under the voice track."""
import wave
import numpy as np

SR = 24000
rng = np.random.default_rng(7)


def _env(n, attack=0.005, decay=None):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1)
    d = np.exp(-t / decay) if decay else 1
    return a * d


def _lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def _sweep(f0, f1, dur):
    n = int(dur * SR)
    f = np.linspace(f0, f1, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def pop():
    x = _sweep(950, 280, 0.09)
    return x * _env(len(x), 0.002, 0.03) * 0.8


def whoosh():
    n = int(0.32 * SR)
    x = _lowpass(rng.standard_normal(n), 18)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    return x * shape * 0.5


def ding():
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1760, 0.6), (2640, 0.25), (3520, 0.15)))
    return x * _env(n, 0.002, 0.25) * 0.5


def sparkle():
    out = np.zeros(int(0.7 * SR))
    for i, f in enumerate((2093, 2637, 3136, 4186)):
        s = int(i * 0.08 * SR)
        n = int(0.3 * SR)
        t = np.arange(n) / SR
        out[s:s + n] += np.sin(2 * np.pi * f * t) * _env(n, 0.002, 0.07) * 0.3
    return out


def poof():
    n = int(0.45 * SR)
    x = _lowpass(rng.standard_normal(n), 40)
    return x * _env(n, 0.01, 0.12) * 1.2


def thunder():
    n = int(1.4 * SR)
    x = _lowpass(_lowpass(rng.standard_normal(n), 60), 60)
    return x * _env(n, 0.03, 0.45) * 3.0


def boing():
    x = _sweep(180, 420, 0.35) * np.sin(np.linspace(0, 40, int(0.35 * SR)))
    return x * _env(len(x), 0.005, 0.15) * 0.5


def cheer():
    # bright major arpeggio
    out = np.zeros(int(0.8 * SR))
    for i, f in enumerate((523, 659, 784, 1047)):
        s = int(i * 0.07 * SR)
        n = int(0.45 * SR)
        t = np.arange(n) / SR
        out[s:s + n] += (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * _env(n, 0.003, 0.12) * 0.3
    return out


def sad():
    # descending "wah wah"
    out = []
    for f in (392, 370, 349, 311):
        x = _sweep(f, f * 0.97, 0.32)
        out.append(x * _env(len(x), 0.02, 0.2) * 0.35)
    return np.concatenate(out)


def stamp():
    n = int(0.25 * SR)
    x = _lowpass(rng.standard_normal(n), 8) + _sweep(160, 60, 0.25)
    return x * _env(n, 0.001, 0.05) * 0.9


def tick():
    x = _sweep(2400, 1800, 0.03)
    return x * _env(len(x), 0.001, 0.01) * 0.6


def cash():
    return np.concatenate([ding()[: int(0.15 * SR)], ding()[: int(0.6 * SR)] * 1.2])


def buzzer():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.25
    return _lowpass(x, 6) * _env(n, 0.005, 0.3)


def record_scratch():
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3.2 * t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + _lowpass(rng.standard_normal(n), 3) * 0.4
    return x * _env(n, 0.005, 0.25) * 0.8


def gasp():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    noise = _lowpass(rng.standard_normal(n), 5) - _lowpass(rng.standard_normal(n), 30)
    shape = np.clip(t / 0.08, 0, 1) * np.exp(-np.clip(t - 0.08, 0, None) / 0.12)
    return noise * shape * 1.4


def ooh():
    # crowd "ooooh": many detuned voices with a falling pitch and a vowel-ish formant
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for i in range(9):
        f0 = 200 + rng.random() * 160
        f = f0 * (1.15 - 0.25 * t / t[-1])
        ph = 2 * np.pi * np.cumsum(f) / SR
        out += np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    out = _lowpass(out, 12)
    return out * np.sin(np.linspace(0, np.pi, n)) ** 1.5 * 0.09


def slide_up():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = np.linspace(500, 1800, n) * (1 + 0.02 * np.sin(2 * np.pi * 9 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.01, 0.4) * 0.45


def slide_down():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f = np.linspace(1700, 300, n) * (1 + 0.02 * np.sin(2 * np.pi * 9 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.01, 0.5) * 0.45


def _ks(f, dur, decay=0.996):
    """Karplus-Strong plucked string"""
    n = int(dur * SR)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out


def harp():
    notes = [523, 659, 784, 1047, 1319, 1568, 2093]
    out = np.zeros(int(1.6 * SR))
    for i, f in enumerate(notes):
        s = int(i * 0.06 * SR)
        x = _ks(f, 1.0)
        out[s:s + len(x)] += x * 0.25
    return out


def register():
    n = int(0.25 * SR)
    drawer = _lowpass(rng.standard_normal(n), 4) * _env(n, 0.002, 0.06) * 0.6
    return np.concatenate([drawer, ding() * 1.2])


def dun():
    out = []
    for i, (f, d) in enumerate(((98, 0.32), (92, 0.32), (73, 1.3))):
        n = int(d * SR)
        t = np.arange(n) / SR
        x = sum(np.sign(np.sin(2 * np.pi * f * k * t)) / k for k in (1, 1.5, 2))
        x = _lowpass(_lowpass(x, 14), 14)
        out.append(x * _env(n, 0.01, d * 0.5) * 0.35)
        out.append(np.zeros(int(0.06 * SR)))
    return np.concatenate(out)


def pow_():
    n = int(0.5 * SR)
    hit = _lowpass(rng.standard_normal(n), 6) * _env(n, 0.001, 0.05)
    boom = _sweep(140, 40, 0.5) * _env(n, 0.001, 0.18)
    return (hit * 0.9 + boom * 1.2)


def swish():
    n = int(0.18 * SR)
    x = _lowpass(rng.standard_normal(n), 6) - _lowpass(rng.standard_normal(n), 40)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 3
    return x * shape * 0.9


def splat():
    n = int(0.35 * SR)
    x = _lowpass(rng.standard_normal(n), 25) * _env(n, 0.002, 0.08) * 1.6
    return x + _sweep(260, 90, 0.35) * _env(n, 0.002, 0.1) * 0.6


def heartbeat():
    out = np.zeros(int(0.8 * SR))
    for st, a in ((0, 1.0), (0.18, 0.7)):
        x = _sweep(80, 45, 0.15) * _env(int(0.15 * SR), 0.003, 0.05) * a
        i = int(st * SR)
        out[i:i + len(x)] += x
    return out


def twinkle():
    return sparkle() * 1.2


SOUNDS = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_")
          and k not in ("build_mix", "read_wav")}
SOUNDS["pow"] = pow_


def read_wav(path):
    with wave.open(path) as w:
        assert w.getframerate() == SR, w.getframerate()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        if w.getnchannels() == 2:
            d = d.reshape(-1, 2).mean(1)
    return d.astype(np.float32) / 32768


def build_mix(voice_path, events, out_path, sfx_gain=0.22):
    v = read_wav(voice_path)
    track = np.zeros(len(v) + SR * 2, dtype=np.float32)
    cache = {}
    for t, name, gain in events:
        if name not in cache:
            cache[name] = SOUNDS[name]().astype(np.float32)
        s = cache[name]
        i = int(t * SR)
        if i >= len(track):
            continue
        j = min(len(track), i + len(s))
        track[i:j] += s[: j - i] * gain * sfx_gain
    track = 0.45 * np.tanh(track / 0.45)  # keep loud hits from swamping the voice
    track[: len(v)] += v
    peak = np.abs(track).max()
    if peak > 0.98:
        track *= 0.98 / peak
    with wave.open(out_path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())
