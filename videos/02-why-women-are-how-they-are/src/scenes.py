"""Video 02: Why Women Are How They Are
Chaaya style: AI sprite cast (hero "Mentor" + cast) on code-drawn props, section themes, transitions,
punch-ins, impacts, kinetic text. One shot per beat; every visual event is pinned to a spoken word via at().
API: reference/engine-api.md"""
import json, math, os, random
import cairo
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
        if x["s"] >= after - 0.05 and x["w"].lower().strip(".,!?…:;\"'-") == w:
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

# Relative heights
REL = {
    "cry": 0.72, "propose": 0.8, "search": 0.88, "love": 0.95, "shocked": 0.95,
    "boy": 0.6, "girl": 0.58, "old_mentor_sit": 0.8, "old_mentor_search": 0.95, "mom": 0.93,
    "shy": 0.92, "shy_shrug": 0.92, "bride": 0.97, "guy_1": 0.95, "guy_2": 0.95,
    "pregnant": 1.0, "nursing_mom": 1.0, "warrior": 1.04, "queen": 1.02,
    "farm_boy": 0.98, "village_girl": 0.96, "handsome_broke": 1.0, "genius": 1.0
}


def hero(c, pose, x, y, t, s=1.0, **kw):
    sprite(c, MENTOR.pose[pose], x, y, HERO_H * s * REL.get(pose, 1.0), t=t, **kw)


def cast(c, pose, x, y, t, s=1.0, **kw):
    sprite(c, CAST.pose[pose], x, y, CAST_H * s * REL.get(pose, 1.0), t=t, **kw)


def hface(c, name, x, y, size, t, born=None, rot=-4):
    face_card(c, MENTOR.face[name], x, y, size, t, born=born, rot=rot)


# ------------------------------------------------------------------ custom props
BOOK_PATH = os.path.join(HERE, "..", "assets", "book_cover.png")
BOOK = cairo.ImageSurface.create_from_png(BOOK_PATH)


def book_cover(c, x, y, s, t, rot=0.0):
    w, h = BOOK.get_width(), BOOK.get_height()
    with xf(c, x, y, s=s, rot=rot):
        rrect(c, -w / 2 + 18, -h / 2 + 22, w, h, 12); setc(c, INK[:3] + (0.85,)); c.fill()
        c.save()
        rrect(c, -w / 2, -h / 2, w, h, 12); c.clip()
        c.set_source_surface(BOOK, -w / 2, -h / 2); c.paint()
        k = (t * 0.45) % 1.6 - 0.3
        sx = -w / 2 + w * k * 1.6
        g = cairo.LinearGradient(sx - 120, -h / 2, sx + 120, h / 2)
        g.add_color_stop_rgba(0, 1, 1, 1, 0)
        g.add_color_stop_rgba(0.5, 1, 1, 1, 0.35)
        g.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.set_source(g); c.paint()
        c.restore()
        rrect(c, -w / 2, -h / 2, w, h, 12); fs(c, None, 8)


def down_arrow(c, x, y, s, col=DARKRED):
    with xf(c, x, y, s=s):
        poly(c, [(-30, -150), (30, -150), (30, 20), (85, 20), (0, 130), (-85, 20), (-30, 20)])
        fs(c, col)


def shield(c, x, y, s=1.0, col="#3B6FD1"):
    fill = hexc(col) if isinstance(col, str) else col
    with xf(c, x, y, s=s):
        poly(c, [(-80, -100), (80, -100), (90, 0), (0, 120), (-90, 0)])
        fs(c, fill, 8)
        poly(c, [(-60, -80), (60, -80), (70, 0), (0, 95), (-70, 0)])
        fs(c, hexc("#FFE680"), 4)


def rain(c, t, n=46, seed=2):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.random() * 1080
        y0 = ((t * 1000 + rnd.random() * 2000) % 1500) + 500
        limb(c, [(x0, y0), (x0 - 10, y0 + 40)], 3, hexc("#5DADE2"))


def bell_curve(c, x0, x1, y_base, h_max, p_draw=1.0):
    pts = []
    n = 60
    for i in range(int(n * p_draw) + 1):
        frac = i / n
        px = x0 + (x1 - x0) * frac
        # Gaussian curve centered at 0.5
        u = (frac - 0.5) / 0.16
        py = y_base - h_max * math.exp(-0.5 * u * u)
        pts.append((px, py))
    if len(pts) >= 2:
        limb(c, pts, 12, hexc("#3B6FD1"))


# ================================================================== 0. Hook
T_MISTAKE = at("mistake")
T_THINK = at("think")
T_COLD = at("cold")
T_DEFECTIVE = at("defective")
T_EVO = at("evolutionary")


@shot(0, L(1) - 0.05, theme="grey", trans="cut",
      sfx=[(0.0, "pow", 0.8), (T_MISTAKE, "gasp", 0.9), (T_THINK, "boing", 0.8),
           (T_DEFECTIVE, "buzzer", 1.0), (T_EVO, "pow", 1.2), (T_EVO + 0.1, "ding", 0.8)])
def s_hook(c, t, lt):
    cam(c, t, lt, 14.5, 1.0, 1.04, focus=(540, 1200),
        punches=[(T_MISTAKE, 0.12, (380, 1100)), (T_EVO, 0.20, (540, 1100))],
        shakes=[(T_MISTAKE, 10), (T_DEFECTIVE, 12)])

    # Characters
    if t < T_THINK:
        hero(c, "facepalm", 360, 1680, t, born=0.1)
    elif t < T_EVO:
        hero(c, "shrug", 360, 1680, t, born=T_THINK)
    else:
        hero(c, "hips", 360, 1680, t, born=T_EVO)

    cast(c, "smart", 760, 1680, t, flip=True, born=0.3)

    # Visual elements
    if t > T_MISTAKE and t < T_EVO:
        thought_cloud(c, 360, 850, 360, 300, from_xy=(360, 1150), scale=pop(t, T_MISTAKE, 0.35))
        slam(c, "LOGIC = MAN?", 360, 850, 48, t, T_MISTAKE, col=WHITE, bg=DARKRED, rot=-3)

    if t > T_DEFECTIVE:
        slam(c, "NOT DEFECTIVE!", 540, 520, 72, t, T_DEFECTIVE, col=WHITE, bg=DARKRED, rot=3)

    if t > T_EVO:
        light_rays(c, 540, 1100, t, "#FFD970", alpha=0.45, r=1100)
        impact(c, 540, 1380, t, T_EVO, label="EVOLUTION", col=hexc("#F5C542"), size=220, dur=99)

    c.save(); c.identity_matrix()
    title_slam(c, t, "Why Women Are How They Are", "(The Evolutionary Truth)", y=290)
    c.restore()


# ================================================================== 1. 70,000 Calories & Pregnancy
T_BURDEN = at("brutal", L(1))
T_MONTHS = at("months", L(1))
T_70K = at("70", L(1))
T_DEATH = at("death", L(1))


@shot(L(1) - 0.05, L(2) - 0.05, theme="red", trans="splat",
      sfx=[(L(1), "swish", 0.8), (T_BURDEN, "pow", 1.0), (T_70K, "register", 1.1),
           (T_DEATH, "thunder", 1.2), (T_DEATH + 0.1, "dun", 1.0)])
def s_burden(c, t, lt):
    cam(c, t, lt, 11.5, 1.0, 1.05, focus=(540, 1200),
        punches=[(T_70K, 0.22, (680, 880)), (T_DEATH, 0.25, (540, 1200))],
        shakes=[(T_70K, 12), (T_DEATH, 18)])

    cast(c, "pregnant", 380, 1680, t, born=L(1) + 0.1)
    hero(c, "shocked", 760, 1680, t, flip=True, born=L(1) + 0.2)

    if t > T_MONTHS:
        slam(c, "9 MONTHS", 720, 680, 64, t, T_MONTHS, col=WHITE, bg=DARKRED, rot=-4)

    if t > T_70K:
        slam(c, "70,000 KCAL!", 720, 880, 76, t, T_70K, col=WHITE, bg=hexc("#E67E22"), rot=3)
        flames(c, 720, 1020, 240, t, h=140)

    if t > T_DEATH:
        impact(c, 540, 1420, t, T_DEATH, label="HIGH RISK", col=hexc("#C0392B"), size=210, dur=99)


# ================================================================== 2. Vulnerability Post-Childbirth
T_VULN = at("vulnerable", L(2))
T_HUNT = at("hunt", L(2))
T_SEX = at("sex", L(2))
T_DIE = at("die", L(2))


@shot(L(2) - 0.05, L(3) - 0.05, theme="purple", trans="whip",
      sfx=[(L(2), "swish", 0.8), (T_VULN, "harp", 0.9), (T_HUNT, "buzzer", 0.8),
           (T_SEX, "buzzer", 0.9), (T_DIE, "dun", 1.2), (T_DIE + 0.1, "sad", 0.9)])
def s_vulnerable(c, t, lt):
    cam(c, t, lt, 14.5, 1.0, 1.04, focus=(540, 1250),
        punches=[(T_DIE, 0.22, (540, 1300))], shakes=[(T_DIE, 16)])

    cast(c, "nursing_mom", 360, 1680, t, born=L(2) + 0.1)
    hero(c, "rain", 760, 1680, t, flip=True, born=L(2) + 0.3)

    storm_cloud(c, 540, 420, 1.2, t)
    rain(c, t, n=24, seed=5)

    slam(c, "TOTAL DEPENDENCY", 540, 620, 64, t, T_VULN, col=WHITE, bg=DARKRED, rot=-2)

    # Checklist
    if t > T_HUNT:
        text_card(c, 680, 840, "Cannot Hunt: YES", pop(t, T_HUNT, 0.2), size=44, col=WHITE, bg=hexc("#C0392B"))
        x_badge(c, 880, 840, 0.8, pop(t, T_HUNT, 0.2))

    if t > T_SEX:
        text_card(c, 680, 960, "No Sex Leverage", pop(t, T_SEX, 0.2), size=44, col=WHITE, bg=hexc("#C0392B"))
        x_badge(c, 920, 960, 0.8, pop(t, T_SEX, 0.2))

    if t > T_DIE:
        impact(c, 540, 1380, t, T_DIE, label="LIFE OR DEATH", col=DARKRED, size=210, dur=99)


# ================================================================== 3. Male Competition
T_MEN_COMP = at("ruthlessly", L(3))
T_PHYS = at("physically", L(3))
T_SOC = at("socially", L(3))
T_SEX_COMP = at("sexually", L(3))
T_REPRO = at("reproduce", L(3))


@shot(L(3) - 0.05, L(4) - 0.05, theme="gold", trans="flip",
      sfx=[(L(3), "pow", 0.9), (T_MEN_COMP, "pow", 1.1), (T_PHYS, "whoosh", 0.8),
           (T_SOC, "ding", 0.8), (T_SEX_COMP, "harp", 0.8), (T_REPRO, "cheer", 1.0)])
def s_competition(c, t, lt):
    cam(c, t, lt, 12.5, 1.0, 1.05, focus=(540, 1200),
        punches=[(T_MEN_COMP, 0.15, (540, 600)), (T_REPRO, 0.18, (540, 1400))])

    cast(c, "warrior", 280, 1680, t, born=L(3) + 0.1)
    cast(c, "chad", 800, 1680, t, flip=True, born=L(3) + 0.2)
    hero(c, "flex", 540, 1720, t, s=0.88, born=L(3) + 0.4)

    slam(c, "MALE COMPETITION", 540, 440, 68, t, T_MEN_COMP, col=WHITE, bg=DARKRED, rot=2)

    # 3 Pillars
    if t > T_PHYS:
        slam(c, "1. PHYSICAL", 540, 660, 48, t, T_PHYS, col=WHITE, bg=hexc("#D35400"), rot=-2)
    if t > T_SOC:
        slam(c, "2. SOCIAL STATUS", 540, 770, 48, t, T_SOC, col=WHITE, bg=hexc("#2980B9"), rot=2)
    if t > T_SEX_COMP:
        slam(c, "3. SEXUAL CHARM", 540, 880, 48, t, T_SEX_COMP, col=WHITE, bg=hexc("#8E44AD"), rot=-1)

    if t > T_REPRO:
        confetti(c, t, T_REPRO)
        impact(c, 540, 1380, t, T_REPRO, label="WINNER REPRODUCES", col=hexc("#F5C542"), size=180, dur=99)


# ================================================================== 4. Survival Software
T_SOFTWARE = at("software", L(4))


@shot(L(4) - 0.05, L(5) - 0.05, theme="cream", trans="iris",
      sfx=[(L(4), "swish", 0.8), (T_SOFTWARE, "pow", 1.2), (T_SOFTWARE + 0.05, "register", 0.8)])
def s_software(c, t, lt):
    cam(c, t, lt, 6.5, 1.0, 1.04, focus=(540, 1200), punches=[(T_SOFTWARE, 0.16, (540, 1000))])

    hero(c, "crossed", 540, 1680, t, born=L(4) + 0.1)

    # Split Column Cards
    p = pop(t, L(4) + 0.2, 0.4)
    if p:
        with xf(c, 240, 950, s=p):
            rrect(c, -180, -220, 360, 440, 16); fs(c, hexc("#2980B9"), 6)
            text(c, "MEN", 0, -140, 56, WHITE, bold=True, align="center")
            text(c, "Risk-Takers", 0, -60, 38, WHITE, bold=False, align="center")
            text(c, "Competitive", 0, 10, 38, WHITE, bold=False, align="center")
            text(c, "Dominant", 0, 80, 38, WHITE, bold=False, align="center")

        with xf(c, 840, 950, s=p):
            rrect(c, -180, -220, 360, 440, 16); fs(c, hexc("#C0392B"), 6)
            text(c, "WOMEN", 0, -140, 56, WHITE, bold=True, align="center")
            text(c, "Safety-First", 0, -60, 38, WHITE, bold=False, align="center")
            text(c, "Nurturing", 0, 10, 38, WHITE, bold=False, align="center")
            text(c, "Gatekeeper", 0, 80, 38, WHITE, bold=False, align="center")

    slam(c, "SURVIVAL SOFTWARE", 540, 480, 68, t, T_SOFTWARE, col=WHITE, bg=DARKRED, rot=2)


# ================================================================== 5. Dominance & Submission
T_DOM = at("dominance", L(5))
T_TRIBES = at("tribes", L(5))
T_ATTRACT = at("attractive", L(5))


@shot(L(5) - 0.05, L(6) - 0.05, theme="red", trans="whip",
      sfx=[(L(5), "pow", 0.9), (T_DOM, "pow", 1.1), (T_TRIBES, "thunder", 0.9),
           (T_ATTRACT, "harp", 1.1), (T_ATTRACT + 0.1, "heartbeat", 1.0)])
def s_dominance(c, t, lt):
    cam(c, t, lt, 15.5, 1.0, 1.05, focus=(540, 1200),
        punches=[(T_DOM, 0.16, (320, 1100)), (T_ATTRACT, 0.18, (740, 1100))])

    cast(c, "warrior", 320, 1680, t, born=L(5) + 0.1)
    cast(c, "village_girl", 740, 1680, t, flip=True, born=L(5) + 0.2)
    hero(c, "coffee", 540, 1720, t, s=0.82, born=L(5) + 0.4)

    shield(c, 480, 1200, s=pop(t, T_DOM, 0.35))

    slam(c, "1. DOMINANCE & SUBMISSION", 540, 440, 56, t, T_DOM, col=WHITE, bg=DARKRED, rot=-2)

    if t > T_TRIBES:
        slam(c, "PROTECTION = SURVIVAL", 540, 620, 52, t, T_TRIBES, col=WHITE, bg=hexc("#D35400"), rot=2)

    if t > T_ATTRACT:
        heart_burst(c, 740, 1100, t, T_ATTRACT, n=12, r=280)
        impact(c, 540, 1400, t, T_ATTRACT, label="HARDCODED DESIRE", col=hexc("#F5C542"), size=180, dur=99)


# ================================================================== 6. Hypergamy
T_HYPER = at("hypergamy", L(6))
T_GATE = at("gatekeepers", L(6))
T_UP = at("up", at("made", L(6)))
T_STATUS = at("status", L(6))


@shot(L(6) - 0.05, L(7) - 0.05, theme="gold", trans="splat",
      sfx=[(L(6), "swish", 0.8), (T_HYPER, "pow", 1.2), (T_GATE, "ding", 0.9),
           (T_UP, "slide_up", 1.1), (T_STATUS, "cheer", 0.9)])
def s_hypergamy(c, t, lt):
    cam(c, t, lt, 12.5, 1.0, 1.05, focus=(540, 1200),
        punches=[(T_HYPER, 0.20, (540, 480)), (T_UP, 0.18, (760, 1000))])

    cast(c, "woman_c", 280, 1680, t, born=L(6) + 0.1)
    cast(c, "chad", 780, 1500, t, flip=True, born=L(6) + 0.2)
    cast(c, "guy_1", 540, 1680, t, s=0.88, born=L(6) + 0.3)

    slam(c, "2. HYPERGAMY", 540, 440, 68, t, T_HYPER, col=WHITE, bg=DARKRED, rot=2)

    if t > T_GATE:
        slam(c, "WOMEN = GATEKEEPERS", 320, 800, 46, t, T_GATE, col=WHITE, bg=hexc("#8E44AD"), rot=-3)

    if t > T_UP:
        trend_arrow(c, 540, 1100, 1.2, up=True, p=prog(t, T_UP, 0.4))
        slam(c, "MATE UP!", 780, 800, 56, t, T_UP, col=WHITE, bg=GREEN, rot=4)

    if t > T_STATUS:
        impact(c, 540, 1420, t, T_STATUS, label="TALLER • STRONGER • RICHER", col=hexc("#F5C542"), size=150, dur=99)


# ================================================================== 7. King vs Queen
T_KING = at("king", L(7))
T_VILLAGE = at("village", L(7))
T_QUEEN = at("queen", L(7))
T_NEVER = at("never", L(7))
T_FARM = at("farm", L(7))
T_LOOK_UP = at("look", L(7))


@shot(L(7) - 0.05, L(8) - 0.05, theme="blue", trans="flip",
      sfx=[(L(7), "pow", 0.9), (T_KING, "ding", 0.9), (T_VILLAGE, "cheer", 0.9),
           (T_QUEEN, "pow", 1.0), (T_NEVER, "buzzer", 1.2), (T_LOOK_UP, "slide_up", 1.0)])
def s_king_queen(c, t, lt):
    cam(c, t, lt, 10.5, 1.0, 1.04, focus=(540, 1200),
        punches=[(T_VILLAGE, 0.15, (270, 1200)), (T_NEVER, 0.22, (810, 1200))],
        shakes=[(T_NEVER, 14)])

    # Split divider line
    limb(c, [(540, 400), (540, 1800)], 8, hexc("#BDC3C7"))

    # Left: King + Village Girl (YES)
    cast(c, "chad", 200, 1680, t, born=L(7) + 0.1)
    cast(c, "village_girl", 380, 1680, t, flip=True, born=L(7) + 0.2)
    text(c, "KING + PEASANT", 270, 580, 46, hexc("#27AE60"), bold=True, align="center")
    checkmark(c, 270, 720, 1.1, pop(t, T_VILLAGE, 0.35))

    # Right: Queen + Farm Boy (NO)
    cast(c, "queen", 700, 1680, t, born=L(7) + 0.3)
    cast(c, "farm_boy", 880, 1680, t, flip=True, born=L(7) + 0.4)
    text(c, "QUEEN + FARM BOY", 810, 580, 46, hexc("#C0392B"), bold=True, align="center")
    if t > T_NEVER:
        x_badge(c, 810, 720, 1.1, pop(t, T_NEVER, 0.35))

    slam(c, "THE ASYMMETRY", 540, 440, 64, t, L(7) + 0.3, col=WHITE, bg=DARKRED, rot=0)

    if t > T_LOOK_UP:
        impact(c, 540, 1420, t, T_LOOK_UP, label="WIRED TO LOOK UP", col=hexc("#F5C542"), size=180, dur=99)


# ================================================================== 8. Resource Stability
T_RES = at("resource", L(8))
T_FEED = at("feed", L(8))
T_JOHN = at("john", L(8))
T_POTENTIAL = at("potential", L(8))
T_NEVER_MAN = at("never", T_POTENTIAL)


@shot(L(8) - 0.05, L(9) - 0.05, theme="cream", trans="whip",
      sfx=[(L(8), "swish", 0.8), (T_RES, "pow", 1.0), (T_FEED, "buzzer", 0.9),
           (T_JOHN, "harp", 1.0), (T_POTENTIAL, "record_scratch", 1.1), (T_NEVER_MAN, "boing", 0.9)])
def s_resource(c, t, lt):
    cam(c, t, lt, 16.5, 1.0, 1.04, focus=(540, 1200),
        punches=[(T_RES, 0.15, (540, 460)), (T_POTENTIAL, 0.22, (340, 1100))],
        shakes=[(T_POTENTIAL, 12)])

    cast(c, "handsome_broke", 280, 1680, t, born=L(8) + 0.1)
    cast(c, "woman_a", 540, 1680, t, flip=True, born=L(8) + 0.2)
    cast(c, "bad_wife_money", 800, 1680, t, flip=True, born=L(8) + 0.3)

    slam(c, "3. RESOURCE STABILITY", 540, 440, 60, t, T_RES, col=WHITE, bg=DARKRED, rot=-2)

    if t > T_JOHN:
        p_b = pop(t, T_JOHN, 0.3)
        if p_b:
            with xf(c, 460, 780, s=p_b):
                rrect(c, -210, -100, 420, 200, 20); fs(c, WHITE, 6)
                poly(c, [(50, 100), (90, 150), (90, 100)]); fs(c, WHITE, 6)
                text(c, "\"John is handsome...", 0, -30, 36, INK, bold=True, align="center")
                text(c, "but lacks earning potential!\"", 0, 35, 30, hexc("#C0392B"), bold=True, align="center")

    if t > T_POTENTIAL:
        money_bag(c, 800, 1200, 1.1)
        big_x(c, 280, 1150, 110, pop(t, T_POTENTIAL, 0.25))

    if t > T_NEVER_MAN:
        impact(c, 540, 1420, t, T_NEVER_MAN, label="MEN VALUE BEAUTY", col=hexc("#F5C542"), size=180, dur=99)


# ================================================================== 9. Emotional Attunement
T_EMO = at("emotional", L(9))
T_RADAR = at("intelligence", L(9))
T_CRIES = at("cries", L(9))
T_HOW = at("how", L(9))


@shot(L(9) - 0.05, L(10) - 0.05, theme="pink", trans="iris",
      sfx=[(L(9), "swish", 0.8), (T_EMO, "harp", 1.0), (T_RADAR, "ding", 0.9),
           (T_CRIES, "gasp", 0.9), (T_HOW, "pow", 1.2), (T_HOW + 0.05, "record_scratch", 0.9)])
def s_emotional(c, t, lt):
    cam(c, t, lt, 18.0, 1.0, 1.04, focus=(540, 1200),
        punches=[(T_HOW, 0.24, (540, 520))], shakes=[(T_HOW, 16)])

    cast(c, "smart", 340, 1680, t, born=L(9) + 0.1)
    hero(c, "shocked", 760, 1680, t, flip=True, born=L(9) + 0.2)

    slam(c, "4. EMOTIONAL RADAR", 540, 440, 60, t, T_EMO, col=WHITE, bg=DARKRED, rot=2)

    # Radar waves from woman
    if t > T_RADAR:
        for i in range(3):
            rp = (lt * 0.8 + i / 3) % 1
            c.arc(340, 1150, 120 + 260 * rp, -math.pi / 3, math.pi / 3)
            c.set_source_rgba(0.23, 0.44, 0.82, 0.8 * (1 - rp))
            c.set_line_width(8)
            c.stroke()

    # Words vs Tone
    p = pop(t, T_RADAR + 0.2, 0.35)
    if p:
        text_card(c, 540, 720, "WORDS: 7%", p, size=42, col=WHITE, bg=hexc("#7F8C8D"))
        text_card(c, 540, 810, "TONE & CUES: 93%", p, size=52, col=WHITE, bg=hexc("#C0392B"))

    if t > T_HOW:
        slam(c, "HOW YOU SAID IT!", 540, 1380, 72, t, T_HOW, col=WHITE, bg=DARKRED, rot=-3)


# ================================================================== 10. Bell Curve Variance
T_VAR = at("variance", L(10))
T_GENIUS = at("geniuses", L(10))
T_HOMELESS = at("homeless", L(10))
T_NEURO = at("neuroticism", L(10))


@shot(L(10) - 0.05, L(11) - 0.05, theme="grey", trans="whip",
      sfx=[(L(10), "swish", 0.8), (T_VAR, "pow", 1.0), (T_GENIUS, "ding", 1.0),
           (T_HOMELESS, "dun", 0.9), (T_NEURO, "swish", 0.8)])
def s_variance(c, t, lt):
    cam(c, t, lt, 15.0, 1.0, 1.04, focus=(540, 1200),
        punches=[(T_GENIUS, 0.16, (840, 1300)), (T_HOMELESS, 0.16, (240, 1300))])

    cast(c, "old_mentor_cry", 200, 1680, t, born=L(10) + 0.1)
    cast(c, "woman_b", 540, 1680, t, born=L(10) + 0.2)
    cast(c, "genius", 840, 1680, t, flip=True, born=L(10) + 0.3)

    slam(c, "5. THE VARIANCE CURVE", 540, 440, 58, t, T_VAR, col=WHITE, bg=DARKRED, rot=-2)

    # Bell curve drawn across canvas
    p_curve = prog(t, T_VAR, 1.2)
    bell_curve(c, 160, 920, 1100, 260, p_curve)

    if t > T_HOMELESS:
        slam(c, "HOMELESS", 200, 880, 42, t, T_HOMELESS, col=WHITE, bg=hexc("#7F8C8D"), rot=-4)

    if t > T_GENIUS:
        lightbulb(c, 840, 750, 0.9, t)
        slam(c, "GENIUSES", 840, 880, 42, t, T_GENIUS, col=WHITE, bg=hexc("#F39C12"), rot=4)

    if t > T_NEURO:
        impact(c, 540, 1420, t, T_NEURO, label="WOMEN CLUSTER AT MEAN", col=hexc("#3B6FD1"), size=160, dur=99)


# ================================================================== 11. Stop Getting Bitter
T_BITTER = at("bitter", L(11))
T_BUDDIES = at("buddies", L(11))
T_DISAPPOINT = at("disappointed", L(11))


@shot(L(11) - 0.05, L(12) - 0.05, theme="red", trans="splat",
      sfx=[(L(11), "pow", 0.9), (T_BITTER, "buzzer", 1.0), (T_BUDDIES, "boing", 0.9),
           (T_DISAPPOINT, "dun", 1.2), (T_DISAPPOINT + 0.1, "sad", 1.0)])
def s_bitter(c, t, lt):
    cam(c, t, lt, 11.0, 1.0, 1.04, focus=(540, 1200),
        punches=[(T_BITTER, 0.16, (540, 500)), (T_DISAPPOINT, 0.22, (380, 1200))],
        shakes=[(T_DISAPPOINT, 16)])

    hero(c, "facepalm" if t < T_DISAPPOINT else "cry", 380, 1680, t, born=L(11) + 0.1)
    cast(c, "woman_a_nag", 760, 1680, t, flip=True, born=L(11) + 0.2)

    slam(c, "STOP BEING BITTER!", 540, 460, 68, t, T_BITTER, col=WHITE, bg=DARKRED, rot=2)

    if t > T_BUDDIES:
        slam(c, "SHE IS NOT YOUR BRO!", 540, 700, 52, t, T_BUDDIES, col=WHITE, bg=hexc("#E74C3C"), rot=-3)
        big_x(c, 540, 920, 140, pop(t, T_BUDDIES, 0.3))

    if t > T_DISAPPOINT:
        impact(c, 540, 1400, t, T_DISAPPOINT, label="STOP FIGHTING BIOLOGY", col=DARKRED, size=180, dur=99)


# ================================================================== 12. Eyes Wide Open
T_PRODUCT = at("product", L(12))
T_BIOLOGY = at("biology", L(12))
T_EYES = at("eyes", L(12))


@shot(L(12) - 0.05, L(13) - 0.05, theme="gold", trans="iris",
      sfx=[(L(12), "swish", 0.8), (T_PRODUCT, "ding", 0.9), (T_BIOLOGY, "harp", 1.0),
           (T_EYES, "pow", 1.2), (T_EYES + 0.1, "cheer", 1.0)])
def s_eyes_open(c, t, lt):
    cam(c, t, lt, 9.5, 1.0, 1.04, focus=(540, 1200),
        punches=[(T_EYES, 0.20, (540, 1100))])

    light_rays(c, 540, 1100, t, "#FFD970", alpha=0.5, r=1200)
    sparkles(c, 540, 1100, 460, t, n=12)

    hero(c, "thumbs", 380, 1680, t, born=L(12) + 0.1)
    cast(c, "good_wife", 740, 1680, t, flip=True, born=L(12) + 0.2)

    slam(c, "CHOOSE WITH REALITY", 540, 480, 64, t, T_BIOLOGY, col=WHITE, bg=GREEN, rot=-2)

    if t > T_EYES:
        eye_icon(c, 540, 850, 1.2, t)
        impact(c, 540, 1380, t, T_EYES, label="EYES WIDE OPEN", col=hexc("#F5C542"), size=220, dur=99)


# ================================================================== 13. Book CTA
T_BOOK_LINE = L(13)
T_BOOK_GUIDE = at("guide", T_BOOK_LINE)
T_LINK_BIO = at("link", T_BOOK_LINE)


@shot(L(13) - 0.05, L(14) - 0.05, theme="gold", trans="splat",
      sfx=[(T_BOOK_LINE, "pow", 1.1), (T_BOOK_GUIDE, "harp", 1.0), (T_LINK_BIO, "pop", 1.0),
           (at("bio", T_BOOK_LINE), "ding", 1.0)])
def s_book(c, t, lt):
    cam(c, t, lt, 6.5, 1.0, 1.04, focus=(540, 1000))
    q = pop(t, T_BOOK_LINE + 0.2, 0.45)
    if q:
        light_rays(c, 620, 880, t, "#FFD970", alpha=0.6 * q, r=1200)
        book_cover(c, 620, 880 + 10 * math.sin(t * 2), 0.88 * q, t, rot=-3 + 2 * math.sin(t * 1.3))
        sparkles(c, 620, 880, 420, t, n=8)

    hero(c, "point_side", 200, 1900, t, s=0.75, born=T_BOOK_LINE)
    slam(c, "LINK IN BIO", 640, 1460, 72, t, T_LINK_BIO, col=WHITE, bg=DARKRED, rot=-2)
    if t > T_LINK_BIO + 0.1:
        down_arrow(c, 640, 1680 + 18 * math.sin(t * 7), pop(t, T_LINK_BIO + 0.1, 0.3) * 0.9)


# ================================================================== 14. Follow for Part 3
T_PART3 = at("three", L(14))
T_FLAGS = at("flags", L(14))
T_FOLLOW = at("follow", L(14))
T_MISS = at("miss", L(14))


@shot(L(14) - 0.05, DURATION + 1, theme="blue", trans="whip",
      sfx=[(L(14), "pow", 1.0), (T_FLAGS, "pop", 1.0), (T_FOLLOW, "boing", 1.1),
           (T_MISS, "ding", 1.0), (T_MISS + 0.05, "cheer", 0.9)])
def s_cta(c, t, lt):
    cam(c, t, lt, 8.0, 1.0, 1.03, punches=[(T_FOLLOW, 0.15, (540, 1100))])

    hero(c, "point_you", 540, 1680, t, born=L(14) + 0.1)

    # Left: What to look for
    cast(c, "good_wife_tray", 180, 1720, t, s=0.75, born=L(14) + 0.2)
    # Right: Red flags to run from
    cast(c, "bad_wife", 900, 1720, t, s=0.75, flip=True, born=L(14) + 0.3)

    slam(c, "PART 3 COMING NEXT", 540, 460, 64, t, T_PART3, col=WHITE, bg=hexc("#2980B9"), rot=-2)

    if t > T_FLAGS:
        slam(c, "BEST TRAITS", 200, 800, 42, t, T_FLAGS, col=WHITE, bg=GREEN, rot=-4)
        slam(c, "RED FLAGS", 880, 800, 42, t, T_FLAGS, col=WHITE, bg=DARKRED, rot=4)

    if t > T_FOLLOW:
        follow_button(c, 540, 1380 + 8 * math.sin(t * 5), 1.2, pressed=pop(t, T_FOLLOW + 0.3, 0.2))
        confetti(c, t, T_FOLLOW)


frame = st.frame
SFX = st.sfx
