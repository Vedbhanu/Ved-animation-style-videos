"""Royalty-free score synthesis. Every sound is generated from maths, nothing is sampled.

Usage in a project's score.py:
    import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/animated-short/engine"))
    from music_lib import Score, CH
    s = Score(158)                      # seconds, must equal the film length
    s.pad(CH["Am"][0], 0, 6.4)          # chord pad
    s.piano(76, 1.2)                    # MIDI note at 1.2 s
    ...
    s.render(sys.argv[1])               # writes stereo 44.1k WAV (reverb + mastering included)

Instruments: pad, strings, choir, piano, bell, pluck, bass, sub, kick, snare, hat, heartbeat,
clock_tick, noise_swell, boom, impact_hit.  Helpers: arp(), drum_loop(), chord_bed().
MIDI: 60 = C4, 69 = A4.  CH maps chord names to (pad notes, bass note).
"""
import wave
import numpy as np

SR = 44100

CH = {
    # minor-key moods
    "Am": ([57, 60, 64], 45), "Dm": ([57, 62, 65], 50), "Em": ([55, 59, 64], 40),
    "Bm": ([54, 59, 62], 47), "Cm": ([55, 60, 63], 48), "Fm": ([56, 60, 65], 41),
    "Gm": ([55, 58, 62], 43), "C#m": ([56, 61, 64], 49), "F#m": ([54, 57, 61], 42),
    # majors
    "C": ([55, 60, 64], 48), "D": ([54, 57, 62], 50), "E": ([52, 56, 59], 40),
    "F": ([53, 57, 60], 41), "G": ([55, 59, 62], 43), "A": ([57, 61, 64], 45),
    "Bb": ([53, 58, 62], 46), "Eb": ([55, 58, 63], 51), "Ab": ([56, 60, 63], 44),
    # colour chords
    "Fmaj7": ([53, 57, 60, 64], 41), "Cmaj7": ([55, 59, 60, 64], 48), "Am9": ([57, 60, 64, 71], 45),
    "Dm7": ([57, 60, 62, 65], 50), "Gsus4": ([55, 60, 62], 43), "Esus4": ([52, 57, 59], 40),
    "Bbmaj7": ([53, 57, 58, 62], 46), "Ebmaj7": ([55, 58, 62, 63], 51),
}


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Score:
    def __init__(self, seconds, seed=7):
        self.dur = seconds
        self.n = int(SR * seconds)
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)
        self.rs = np.random.RandomState(seed)

    # ------------------------------------------------------------ core
    def add(self, sig, t0, amp=1.0, pan=0.0):
        i0 = int(t0 * SR)
        if i0 >= self.n or i0 < 0:
            return
        sig = sig[: self.n - i0]
        self.L[i0:i0 + len(sig)] += sig * amp * (1 - pan)
        self.R[i0:i0 + len(sig)] += sig * amp * (1 + pan)

    @staticmethod
    def _env(n, a, r):
        e = np.ones(n)
        na, nr = min(n, int(a * SR)), min(n, int(r * SR))
        if na:
            e[:na] = np.linspace(0, 1, na)
        if nr:
            e[-nr:] *= np.linspace(1, 0, nr)
        return e

    def _lowpass(self, x, start=0.02, end=0.35):
        """time-varying one-pole lowpass (cheap filter sweep)."""
        n = len(x)
        y = np.zeros(n)
        alpha = np.linspace(start, end, n)
        acc = 0.0
        for i in range(0, n, 128):
            a = alpha[i]
            seg = x[i:i + 128]
            out = np.empty_like(seg)
            for j, v in enumerate(seg):
                acc += a * (v - acc)
                out[j] = acc
            y[i:i + 128] = out
        return y

    # ------------------------------------------------------------ tonal
    def pad(self, midis, t0, dur, amp=0.05, bright=6, a=1.6, r=1.8, pan=0.0):
        """warm detuned chord bed."""
        n = int((dur + r) * SR)
        t = np.arange(n) / SR
        s = np.zeros(n)
        for m in midis:
            for det in (-0.08, 0.0, 0.07):
                f = hz(m + det)
                for k in range(1, bright + 1):
                    s += np.sin(2 * np.pi * f * k * t + k * det * 10) / (k ** 1.6)
        s *= self._env(n, a, r) * (1 + 0.15 * np.sin(2 * np.pi * 0.2 * t))
        self.add(s / (len(midis) * 3), t0, amp, pan)

    def strings(self, midis, t0, dur, amp=0.05, a=0.9, r=1.5, vib=0.12):
        """bowed-string ensemble: saw-ish with vibrato, slower attack."""
        n = int((dur + r) * SR)
        t = np.arange(n) / SR
        s = np.zeros(n)
        for m in midis:
            for det, ph in ((-0.05, 0.0), (0.05, 1.7)):
                f = hz(m + det) * (1 + 0.004 * vib * np.sin(2 * np.pi * 5.2 * t + ph))
                phase = 2 * np.pi * np.cumsum(f) / SR
                for k in range(1, 10):
                    s += np.sin(k * phase) / k * (0.92 ** k)
        s *= self._env(n, a, r)
        self.add(s / (len(midis) * 4), t0, amp)

    def choir(self, midis, t0, dur, amp=0.05, a=1.2, r=2.0):
        """'ooh' vowel pad: harmonics weighted around formants ~400 Hz & ~800 Hz."""
        n = int((dur + r) * SR)
        t = np.arange(n) / SR
        s = np.zeros(n)
        for m in midis:
            f0 = hz(m)
            for det in (-0.1, 0.1):
                f = f0 * 2 ** (det / 12) * (1 + 0.003 * np.sin(2 * np.pi * 4.8 * t))
                phase = 2 * np.pi * np.cumsum(f) / SR
                for k in range(1, 14):
                    fk = f0 * k
                    w = np.exp(-((fk - 400) / 180) ** 2) + 0.6 * np.exp(-((fk - 800) / 250) ** 2) + 0.15 / k
                    s += np.sin(k * phase) * w
        s *= self._env(n, a, r)
        self.add(s / (len(midis) * 3), t0, amp)

    def piano(self, m, t0, amp=0.1, dur=4.0, pan=0.0):
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = hz(m)
        s = np.zeros(n)
        for k in range(1, 8):
            s += np.sin(2 * np.pi * f * k * 1.0007 ** k * t) * np.exp(-t * (0.9 + 0.7 * k)) / k ** 1.3
        s *= np.minimum(1, t / 0.004)
        self.add(s, t0, amp, pan)

    def bell(self, m, t0, amp=0.07, dur=5.0, pan=0.0):
        """inharmonic glassy bell / music box."""
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = hz(m)
        s = np.zeros(n)
        for ratio, a, dec in ((1, 1, 1.2), (2.76, 0.5, 2.0), (5.4, 0.25, 3.5), (8.93, 0.12, 5)):
            s += a * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
        s *= np.minimum(1, t / 0.002)
        self.add(s, t0, amp, pan)

    def pluck(self, m, t0, amp=0.06, pan=0.0, decay=5.0):
        n = int(0.8 * SR)
        t = np.arange(n) / SR
        f = hz(m)
        s = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (decay + 3 * k)) / k for k in range(1, 6))
        s *= np.minimum(1, t / 0.003)
        self.add(s, t0, amp, pan)

    def bass(self, m, t0, dur, amp=0.12):
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = hz(m)
        s = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.8 for k in range(1, 5))
        s *= self._env(n, 0.01, min(0.08, dur / 3)) * np.exp(-t * 1.5)
        self.add(s, t0, amp)

    def sub(self, m, t0, dur, amp=0.1, a=0.5, r=1.0):
        """pure low drone."""
        n = int((dur + r) * SR)
        t = np.arange(n) / SR
        self.add(np.sin(2 * np.pi * hz(m) * t) * self._env(n, a, r), t0, amp)

    # ------------------------------------------------------------ percussion
    def kick(self, t0, amp=0.5):
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        f = 45 + 90 * np.exp(-t * 30)
        self.add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7), t0, amp)

    def snare(self, t0, amp=0.18):
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        noise = self.rs.randn(n)
        noise = noise - np.concatenate([[0], noise[:-1]]) * 0.6
        s = noise * np.exp(-t * 14) * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 20)
        self.add(s, t0, amp)

    def hat(self, t0, amp=0.05, open_=False):
        n = int((0.25 if open_ else 0.06) * SR)
        t = np.arange(n) / SR
        noise = self.rs.randn(n)
        noise = noise - np.concatenate([[0], noise[:-1]])
        self.add(noise * np.exp(-t * (12 if open_ else 60)), t0, amp, pan=0.2)

    def heartbeat(self, t0, amp=0.3):
        self.kick(t0, amp)
        self.kick(t0 + 0.28, amp * 0.6)

    def clock_tick(self, t0, amp=0.08):
        n = int(0.03 * SR)
        t = np.arange(n) / SR
        self.add(np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 300), t0, amp, pan=-0.3)

    def noise_swell(self, t0, dur, amp=0.08, rise=True):
        n = int(dur * SR)
        x = self.rs.randn(n)
        y = self._lowpass(x, 0.02, 0.35) if rise else self._lowpass(x, 0.35, 0.02)
        e = np.linspace(0, 1, n) ** 2 if rise else np.linspace(1, 0, n) ** 2
        self.add(y * e, t0, amp)

    def boom(self, t0, amp=0.6):
        """cinematic low hit (scene punctuation)."""
        self.kick(t0, amp)
        n = int(2.5 * SR)
        t = np.arange(n) / SR
        self.add(np.sin(2 * np.pi * 36 * t) * np.exp(-t * 1.6), t0, amp * 0.6)
        self.noise_swell(t0, 1.2, 0.05, rise=False)

    def impact_hit(self, t0, amp=0.35):
        """short punchy hit for on-screen impacts."""
        self.kick(t0, amp)
        self.snare(t0, amp * 0.5)

    # ------------------------------------------------------------ patterns
    def arp(self, midis, t0, dur, step, amp=0.05, inst="pluck", octave=12):
        notes = [m + octave for m in midis]
        seq = notes + notes[-2:0:-1] if len(notes) > 2 else notes
        k, t = 0, t0
        while t < t0 + dur - 1e-6:
            getattr(self, inst)(seq[k % len(seq)], t, amp, pan=0.35 * (-1) ** k)
            t += step
            k += 1

    def drum_loop(self, t0, dur, bpm, amp=0.4, style="four"):
        """style: four (kick every beat) | half (kick 1, snare 3) | rock (k-s-k-s + hats) | pulse (8ths)."""
        beat = 60.0 / bpm
        t, i = t0, 0
        while t < t0 + dur - 1e-6:
            b = i % 4
            if style == "four":
                self.kick(t, amp)
            elif style == "half":
                if b == 0:
                    self.kick(t, amp)
                if b == 2:
                    self.snare(t, amp * 0.45)
            elif style == "rock":
                self.kick(t, amp) if b in (0, 2) else self.snare(t, amp * 0.45)
                self.hat(t, amp * 0.12)
                self.hat(t + beat / 2, amp * 0.08)
            elif style == "pulse":
                self.kick(t, amp)
                self.hat(t + beat / 2, amp * 0.1)
            t += beat
            i += 1

    def chord_bed(self, prog, t0, chord_len, amp=0.05, inst="pad", with_bass=True):
        for i, name in enumerate(prog):
            notes, b = CH[name]
            getattr(self, inst)(notes, t0 + i * chord_len, chord_len + 0.5, amp)
            if with_bass:
                self.sub(b, t0 + i * chord_len, chord_len, amp * 1.1)

    # ------------------------------------------------------------ output
    def _reverb(self, x, seed, length=2.8, decay=2.4):
        r = np.random.RandomState(seed)
        n = int(length * SR)
        ir = r.randn(n) * np.exp(-np.arange(n) / SR * decay)
        ir[: int(0.02 * SR)] = 0
        size = 1 << int(np.ceil(np.log2(len(x) + n)))
        y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
        return y / np.sqrt(np.sum(ir ** 2)) * 0.9

    def render(self, path, wet=0.45, room=2.8):
        outL = self.L * 0.75 + self._reverb(self.L, 1, room) * wet
        outR = self.R * 0.75 + self._reverb(self.R, 2, room) * wet
        fade = np.ones(self.n)
        nf = int(2.5 * SR)
        fade[-nf:] = np.linspace(1, 0, nf) ** 1.5
        fade[: int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
        out = np.stack([outL * fade, outR * fade], axis=1)
        out = np.tanh(out / np.max(np.abs(out)) * 1.3) / np.tanh(1.3) * 0.89
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((out * 32767).astype(np.int16).tobytes())
        print("music ->", path)
