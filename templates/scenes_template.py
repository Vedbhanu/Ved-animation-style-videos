"""Video NN: <Title>
Chaaya style: AI sprite cast (hero "Mentor" + cast) on code-drawn props, section themes, transitions,
punch-ins, impacts, kinetic text. One shot per beat; every visual event is pinned to a spoken word via at().
Fill the shots from storyboard.md; keep the helpers. API: reference/engine-api.md"""
import json, math, os, random
from toon import *
from stage import Stage

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(HERE, "..", "build", "words.json")))
LINES = json.load(open(os.path.join(HERE, "..", "build", "lines.json")))
DURATION = LINES[-1]["end"] + 0.8
ASSETS = os.path.join(HERE, "..", "..", "..", "assets", "characters")


def at(word, after=0.0, end=False):
    """start (or end) time of the first spoken word matching `word` at/after `after`"""
    w = word.lower()
    for x in WORDS:
        if x["s"] >= after - 0.05 and x["w"].lower().strip(".,!?…:;\"'") == w:
            return x["e"] if end else x["s"]
    raise KeyError(f"{word} after {after}")


def L(i):
    return LINES[i]["start"]


st = Stage()
shot = st.shot

# ------------------------------------------------------------------ sprite cast
MENTOR = SpriteSet(os.path.join(ASSETS, "mentor"))
CAST = SpriteSet(os.path.join(ASSETS, "cast"))
HERO_H, CAST_H = 760, 700
# relative heights for poses that aren't a full standing adult
REL = {"cry": 0.72, "propose": 0.8, "search": 0.88, "love": 0.95, "shocked": 0.95,
       "boy": 0.6, "girl": 0.58, "old_mentor_sit": 0.8, "old_mentor_search": 0.95, "mom": 0.93,
       "shy": 0.92, "shy_shrug": 0.92, "bride": 0.97, "guy_1": 0.95, "guy_2": 0.95}


def hero(c, pose, x, y, t, s=1.0, **kw):
    sprite(c, MENTOR.pose[pose], x, y, HERO_H * s * REL.get(pose, 1.0), t=t, **kw)


def cast(c, pose, x, y, t, s=1.0, **kw):
    sprite(c, CAST.pose[pose], x, y, CAST_H * s * REL.get(pose, 1.0), t=t, **kw)


def hface(c, name, x, y, size, t, born=None, rot=-4):
    face_card(c, MENTOR.face[name], x, y, size, t, born=born, rot=rot)


def gold_person(c, x, y, s=1.0, t=0.0, alpha=1.0, **kw):
    """the Dream Girl: floating angel sprite with a golden glow (overrides the cartoon version)"""
    fy = y - 30 * s - 14 * s * math.sin(t * 2.2)
    g = cairo.RadialGradient(x, fy - 300 * s, 20 * s, x, fy - 300 * s, 430 * s)
    g.add_color_stop_rgba(0, 1, 0.88, 0.35, 0.75 * alpha)
    g.add_color_stop_rgba(1, 1, 0.88, 0.35, 0)
    c.set_source(g); c.arc(x, fy - 300 * s, 430 * s, 0, 2 * math.pi); c.fill()
    sprite(c, CAST.pose["dream_girl"], x, fy, 620 * s, t=t, alpha=alpha, shadow=False, bob=True, seed=3)
    sparkles(c, x, fy - 320 * s, 320 * s, t, n=7, alpha=alpha)


# ------------------------------------------------------------------ small helpers
def enter(t, t0, x0, x1, dur=0.5):
    return x0 + (x1 - x0) * ease_out(prog(t, t0, dur))


def floating_hearts(c, x, y, lt, n=3, spread=60):
    for i in range(n):
        hp = (lt * 0.5 + i / n) % 1
        with xf(c, x + spread * math.sin(i * 2 + lt * 2), y - 260 * hp, s=0.45 + 0.2 * i / n, alpha=1 - hp):
            heart(c)


def box_pile(c, x, y, n):
    cols = ["#C9A66B", "#B5895A", "#D8B98A", "#C9A66B", "#B5895A", "#D8B98A"]
    for i in range(n):
        with xf(c, x + (i % 2) * 14 - 7, y - i * 88, rot=(-3, 4, -2, 3, -4, 2)[i]):
            rrect(c, -95, -88, 190, 88, 6); fs(c, hexc(cols[i]))
            limb(c, [(-35, -84), (35, -84)], 4, hexc("#8A5A3B"))


def qmarks(c, t, t0, pts, col="#3B6FD1", size=100):
    for i, (qx, qy) in enumerate(pts):
        q = pop(t, t0 + 0.12 * i, 0.3)
        if q:
            with xf(c, qx, qy, s=q):
                question_mark(c, 0, 0, size, t + i, col=hexc(col))


def bench(c, x, y, w=420):
    for lx in (-w / 2 + 30, w / 2 - 30):
        limb(c, [(x + lx, y), (x + lx, y - 150)], 16, hexc("#6B4226"))
    rrect(c, x - w / 2, y - 175, w, 34, 8); fs(c, hexc("#B5895A"))
    rrect(c, x - w / 2, y - 300, w, 30, 8); fs(c, hexc("#B5895A"))
    for lx in (-w / 2 + 40, w / 2 - 40):
        limb(c, [(x + lx, y - 175), (x + lx, y - 300)], 12, hexc("#8A5A3B"))


def rain(c, t, n=46, seed=2):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.random() * W
        y0 = ((t * 1000 + rnd.random() * 2000) % 1500) + 500
        limb(c, [(x0, y0), (x0 - 10, y0 + 40)], 3, hexc("#5DADE2"))


# ================================================================== 0. hook (example: replace)
T_KEY = at("important")          # the hook's punch word


@shot(0, L(1) - 0.05, theme="cream", trans="cut",
      sfx=[(0.0, "pow", 0.8), (0.35, "swish", 0.8), (T_KEY, "pow", 1.2)])
def s_hook(c, t, lt):
    cam(c, t, lt, 5, 1.0, 1.05, focus=(420, 1200), punches=[(T_KEY, 0.2, (390, 1000))], shakes=[(T_KEY, 14)])
    hero(c, "hips", 380, 1640, t, born=0.15)
    impact(c, 800, 900, t, T_KEY, label="#1", col="#F5C542", size=170, dur=99)
    c.save(); c.identity_matrix()                 # title is never zoomed/cropped by the camera
    title_slam(c, t, "<LINE 1?>", "(<line 2>)", y=290)
    c.restore()


# ================================================================== 1. example beat (replace)
@shot(L(1) - 0.05, DURATION + 1, theme="gold", trans="whip",
      sfx=[(L(1) + 0.2, "boing", 0.9)])
def s_beat1(c, t, lt):
    cam(c, t, lt, 4, 1.0, 1.05)
    light_rays(c, 540, 1100, t, "#FFE680", alpha=0.4, r=1000)
    cast(c, "good_wife", 360, 1680, t, born=L(1))
    hero(c, "thumbs", 760, 1680, t, flip=True, born=L(1) + 0.3)
    slam(c, "KEY WORD", 540, 700, 96, t, L(1) + 0.4, col=WHITE, bg=GREEN, rot=-4)


frame = st.frame
SFX = st.sfx
