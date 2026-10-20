"""Render a scenes module to MP4 (parallel frame chunks -> concat -> mux voice + SFX + ducked music).

usage: python render.py <project_dir> [--start S] [--end E] [--workers N] [--out file.mp4] [--still T ...]

The project's src/scenes.py must define:
  frame(c, t)       draw the frame at time t
  SFX               list of (time, name, gain)
  DURATION          seconds
Optional: src/score.py (writes build/music.wav when run as `score.py <out.wav>`)
"""
import argparse, importlib.util, os, subprocess, sys, wave
import multiprocessing as mp
import numpy as np

ENGINE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ENGINE)
import toon  # noqa: E402
import sfx  # noqa: E402
import chars  # noqa: E402
import fx  # noqa: E402


def voice_env(path):
    v = sfx.read_wav(path)
    hop = sfx.SR // toon.FPS
    n = len(v) // hop
    rms = np.sqrt(np.mean(v[: n * hop].reshape(n, hop) ** 2, axis=1))
    rms = rms / (np.percentile(rms, 95) + 1e-6)
    env = np.clip((rms - 0.12) * 1.3, 0, 1)
    # light smoothing so the mouth doesn't flicker
    return np.convolve(env, [0.25, 0.5, 0.25], mode="same")


def load(proj):
    spec = importlib.util.spec_from_file_location("scenes", os.path.join(proj, "src", "scenes.py"))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(proj, "src"))
    spec.loader.exec_module(m)
    chars.set_voice_env(voice_env(os.path.join(proj, "build", "voice.wav")))
    return m


def draw(m, t, wobble=True):
    surf, c = toon.new_frame()
    m.frame(c, t)
    surf.flush()
    if wobble:
        fx.boil(surf, t)
    return surf


def chunk(args):
    proj, f0, f1, path = args
    m = load(proj)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{toon.W}x{toon.H}", "-r", str(toon.FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path],
                         stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(bytes(draw(m, f / toon.FPS).get_data()))
    p.stdin.close()
    p.wait()
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proj")
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() - 2))
    ap.add_argument("--out")
    ap.add_argument("--still", type=float, nargs="*")
    a = ap.parse_args()
    proj = os.path.abspath(a.proj)
    build = os.path.join(proj, "build")
    m = load(proj)

    if a.still:
        for t in a.still:
            draw(m, t).write_to_png(os.path.join(build, f"still_{t:06.2f}.png"))
        return

    end = a.end if a.end is not None else m.DURATION
    f0, f1 = int(a.start * toon.FPS), int(end * toon.FPS)
    n = max(1, a.workers)
    step = max(1, (f1 - f0 + n - 1) // n)
    jobs = [(proj, s, min(s + step, f1), os.path.join(build, f"seg_{i:02d}.mp4"))
            for i, s in enumerate(range(f0, f1, step))]
    with mp.Pool(n) as pool:
        segs = pool.map(chunk, jobs)
    lst = os.path.join(build, "segs.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))

    # audio: voice + sfx, then music ducked under the voice
    voice = os.path.join(build, "voice.wav")
    mix = os.path.join(build, "mix.wav")
    sfx.build_mix(voice, m.SFX, mix)
    music = os.path.join(build, "music.wav")
    score = os.path.join(proj, "src", "score.py")
    if os.path.exists(score) and (not os.path.exists(music) or os.path.getmtime(score) > os.path.getmtime(music)):
        subprocess.run([sys.executable, "-I", score, music, ENGINE], check=True)
    out = a.out or os.path.join(build, "render.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
           "-ss", str(a.start), "-t", str(end - a.start), "-i", mix]
    if os.path.exists(music):
        cmd += ["-ss", str(a.start), "-t", str(end - a.start), "-i", music,
                "-filter_complex",
                "[1:a]aresample=44100,aformat=channel_layouts=stereo,asplit=2[v][sc];"
                "[2:a]volume=0.32[m];"
                "[m][sc]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=350[md];"
                "[v][md]amix=inputs=2:normalize=0,volume=1.3,alimiter=limit=0.97[a]",
                "-map", "0:v", "-map", "[a]"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out]
    subprocess.run(cmd, check=True)
    for s in segs:
        os.remove(s)
    print(out)


if __name__ == "__main__":
    main()
