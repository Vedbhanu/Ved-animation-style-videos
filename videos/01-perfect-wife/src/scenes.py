"""Video 01 (v3): Looking for the PERFECT Wife? (She Doesn't Exist)
AI-illustrated sprite cast (hero "Mentor" + supporting cast) on code-drawn props, themes, transitions,
punch-ins, impacts and kinetic text."""
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


# ================================================================== 0. hook
T_MARRY = at("marry")
T_IMPORTANT = at("important")
T_MEN = at("men")
T_WOMAN = at("woman", T_MEN)
T_NOT = at("not", T_WOMAN)
T_EXIST = at("exist", T_WOMAN, end=True)
T_L1 = L(1)


@shot(0, T_MEN - 0.25, theme="cream", trans="cut",
      sfx=[(0.0, "pow", 0.8), (0.35, "swish", 0.8), (T_MARRY, "harp", 1.0), (T_MARRY + 0.05, "ding", 0.6),
           (T_IMPORTANT, "pow", 1.2), (T_IMPORTANT + 0.05, "ooh", 0.8)])
def s_hook(c, t, lt):
    cam(c, t, lt, 5, 1.0, 1.05, focus=(420, 1200),
        punches=[(T_IMPORTANT, 0.22, (390, 1000))], shakes=[(T_IMPORTANT, 14)])
    if t > T_MARRY:
        light_rays(c, 640, 1300, t, "#FFE680", alpha=0.45 * prog(t, T_MARRY, 0.3), r=900)
    impact(c, 820, 900, t, T_IMPORTANT, label="#1", col="#F5C542", size=170, dur=99)
    hero(c, "love" if t > T_MARRY else "hips", 380, 1640, t, born=0.15 if t < T_MARRY else T_MARRY)
    heart_burst(c, 380, 1050, t, T_MARRY, n=10, r=300)
    ring_box(c, 700, 1330 + 14 * math.sin(t * 3), 1.1, prog(t, T_MARRY, 0.25), t)
    c.save(); c.identity_matrix()
    title_slam(c, t, "Looking for the PERFECT Wife?", "(She Doesn't Exist)", y=290)
    c.restore()


@shot(T_MEN - 0.25, T_L1 - 0.05, theme="blue", trans="whip",
      sfx=[(T_WOMAN, "harp", 1.0), (T_NOT, "record_scratch", 1.0), (T_EXIST + 0.15, "poof", 1.2),
           (T_EXIST + 0.2, "gasp", 1.0)])
def s_search(c, t, lt):
    gone = T_EXIST + 0.15
    cam(c, t, lt, 5, 1.0, 1.04, focus=(540, 1200), punches=[(gone, 0.25, (300, 1050))])
    t_walk_end = T_MEN + 0.9
    if t < t_walk_end:
        hero(c, "walk", enter(t, T_MEN - 0.25, -200, 280, 1.1), 1680, t, hop=12)
    elif t < T_WOMAN - 0.1:
        hero(c, "search", 290, 1680, t, born=t_walk_end)
    elif t < gone:
        hero(c, "point_side", 290, 1680, t, born=T_WOMAN - 0.1)
    else:
        hero(c, "shocked", 300, 1680, t, born=gone)
        sweat_flood(c, 300, 1400, t, s=0.9)
    p = pop(t, T_WOMAN - 0.1, 0.4)
    if p and t < gone:
        light_rays(c, 720, 700, t, "#FFE680", alpha=0.35 * p, r=500)
        thought_cloud(c, 720, 720, 520, 600, from_xy=(470, 1020), scale=p)
        with xf(c, 720, 720, s=p):
            gold_person(c, 0, 240, s=0.68, t=t)
        big_x(c, 720, 720, 180, prog(t, T_NOT, 0.25))
    puff(c, 720, 720, prog(t, gone, 0.7), r=240)


# ================================================================== 1. life changes forever
T_MARRY2 = at("marry", T_L1)
T_WHETHER = at("whether", T_L1)
T_BETTER = at("better", T_L1)
T_WORSE = at("worse", T_L1)
T_PICK = at("pick", T_L1)


@shot(T_L1 - 0.05, T_WHETHER - 0.1, theme="pink", trans="iris",
      sfx=[(T_MARRY2, "cheer", 1.0), (T_MARRY2, "harp", 0.8)])
def s_wedding(c, t, lt):
    cam(c, t, lt, 3, 1.0, 1.1, focus=(540, 1250))
    light_rays(c, 540, 1100, t, "#F7A8B8", alpha=0.35, r=1100)
    arch(c, 540, 1660, 820, 1080)
    hero(c, "love" if t > T_MARRY2 else "crossed", 370, 1670, t, s=0.95,
         born=T_L1 + 0.1 if t < T_MARRY2 else T_MARRY2)
    cast(c, "bride", 720, 1670, t, born=T_L1 + 0.3)
    heart_burst(c, 540, 1000, t, T_MARRY2, n=14, r=420)
    confetti(c, t, T_MARRY2, n=70)


@shot(T_WHETHER - 0.1, L(2) - 0.05, theme="cream", trans="whip",
      sfx=[(T_BETTER, "cheer", 0.8), (T_WORSE, "thunder", 1.3), (T_PICK, "boing", 1.0)])
def s_fork(c, t, lt):
    cam(c, t, lt, 4.5, 1.0, 1.04, shakes=[(T_WORSE, 16)])
    pb = pop(t, T_BETTER - 0.1, 0.4)
    pw = pop(t, T_WORSE - 0.1, 0.4)
    if pb:
        light_rays(c, 270, 900, t, "#FFE680", alpha=0.35, r=420)
        with xf(c, 270, 900, s=pb):
            sun(c, -60, -330, 55, t)
            house(c, 0, 0, 0.95, "happy", t)
    if pw:
        with xf(c, 810, 900, s=pw):
            house(c, 0, 0, 0.95, "bad", t)
            storm_cloud(c, 0, -360, 0.85, t)
    flash(c, t, T_WORSE)
    sign(c, 210, 1420, "BETTER", GREEN, direction=-1, s=0.9, p=pb)
    sign(c, 870, 1420, "WORSE", RED, direction=1, s=0.9, p=pw)
    hero(c, "shocked" if t > T_WORSE else "crossed", 540, 1800, t, s=0.85, born=T_WORSE if t > T_WORSE else None)
    if t > T_PICK - 0.1:
        hface(c, "think", 540, 640, 270, t, born=T_PICK - 0.1, rot=3)
        qmarks(c, t, T_PICK + 0.2, ((380, 560), (700, 540), (720, 780)))


# ================================================================== 2. good wife
T_S2 = at("She", L(2) + 1.5)
T_NURT = at("nurture", L(2))
T_AND_MOM = at("and", at("work", T_NURT))
T_ASSET = at("asset", L(2))
T_SEX = at("sexually", T_S2)


@shot(L(2) - 0.05, T_S2 - 0.1, theme="gold", trans="whip",
      sfx=[(T_ASSET, "pow", 1.0), (T_ASSET + 0.05, "register", 0.9), (T_ASSET + 0.2, "cheer", 0.7)])
def s_good_wife(c, t, lt):
    cam(c, t, lt, 2.5, 1.0, 1.05, punches=[(T_ASSET, 0.12, (540, 1100))])
    light_rays(c, 360, 1250, t, "#FFE680", alpha=0.5, r=1000)
    money_rain(c, t, T_ASSET, n=18, seed=3)
    cast(c, "good_wife", 360, 1680, t, s=1.1, born=L(2))
    draw_arrow(c, ((640, 1300), (760, 1260), (960, 1060)), prog(t, T_ASSET, 0.45), col=GREEN, width=22)
    slam(c, "ASSET", 770, 860, 110, t, T_ASSET, col=WHITE, bg=GREEN, rot=-6)
    sparkles(c, 360, 1200, 300, t, n=6)


@shot(T_S2 - 0.1, T_NURT - 0.15, theme="pink", trans="whip",
      sfx=[(T_SEX, "slide_up", 1.0), (T_SEX + 0.1, "ooh", 1.0), (T_SEX + 0.05, "twinkle", 0.7)])
def s_serve(c, t, lt):
    cam(c, t, lt, 3, 1.0, 1.04, punches=[(T_SEX, 0.15, (760, 1150))])
    hot = t > T_SEX
    cast(c, "good_wife_tray", 330, 1680, t, born=T_S2)
    hero(c, "love" if hot else "coffee", 790, 1680, t, s=0.95, flip=True, born=T_SEX if hot else None)
    heart_burst(c, 790, 1100, t, T_SEX, n=14, r=380)
    if hot:
        hface(c, "love", 760, 760, 300, t, born=T_SEX + 0.15, rot=5)


@shot(T_NURT - 0.15, T_AND_MOM - 0.1, theme="gold", trans="flip",
      sfx=[(at("positive", T_NURT), "twinkle", 0.9), (at("home", T_NURT), "cheer", 1.0),
           (at("home", T_NURT), "slide_up", 0.7)])
def s_home(c, t, lt):
    th = at("home", T_NURT)
    cam(c, t, lt, 4.5, 1.0, 1.05)
    light_rays(c, 860, 620, t, "#FFE680", alpha=0.4, r=900)
    sun(c, 860, 620, 70, t)
    house(c, 600, 1350, 1.55, "happy", t)
    sparkles(c, 600, 1050, 380, t, n=7, alpha=prog(t, at("positive", T_NURT), 0.3))
    cast(c, "good_wife", 880, 1720, t, s=0.85, flip=True)
    if t < th:
        hero(c, "walk", enter(t, T_NURT + 0.3, -220, 290, 2.4), 1740, t, s=0.85, hop=10)
    else:
        hero(c, "thumbs", 290, 1740, t, s=0.85, born=th)
        heart_burst(c, 290, 1150, t, th, n=10, r=260)


@shot(T_AND_MOM - 0.1, L(3) - 0.05, theme="gold", trans="whip",
      sfx=[(at("children", T_AND_MOM), "boing", 0.9), (at("children", T_AND_MOM) + 0.2, "boing", 0.8),
           (at("children", T_AND_MOM) + 0.3, "cheer", 0.8)])
def s_mother(c, t, lt):
    cam(c, t, lt, 3, 1.0, 1.05)
    tc = at("children", T_AND_MOM)
    cast(c, "good_wife", 540, 1680, t, s=1.05)
    cast(c, "boy", 230, 1700, t, born=tc)
    cast(c, "girl", 860, 1700, t, born=tc + 0.2)
    heart_burst(c, 540, 1000, t, tc + 0.2, n=12, r=380)
    floating_hearts(c, 540, 1000, lt, 4, 140)


# ================================================================== 3. bad wife
T_S3 = at("She", L(3) + 1.5)
T_HELL = at("hell", T_S3)
T_TAKE = at("take", T_S3)
T_NOTEVEN = at("not", T_TAKE)
T_S3c = at("She", T_NOTEVEN)
T_DIV = at("divorce", T_S3c)
T_LIAB = at("liability", L(3))


@shot(L(3) - 0.05, T_S3 - 0.1, theme="red", trans="splat",
      sfx=[(at("bad", L(3)), "dun", 1.0), (T_LIAB, "pow", 1.1), (T_LIAB + 0.15, "slide_down", 0.8)])
def s_bad_wife(c, t, lt):
    cam(c, t, lt, 2.5, 1.0, 1.05, punches=[(T_LIAB, 0.12, (540, 1100))], shakes=[(T_LIAB, 12)])
    storm_cloud(c, 360, 620, 0.75, t, bolt=True)
    cast(c, "bad_wife", 360, 1690, t, s=1.1, born=L(3))
    draw_arrow(c, ((640, 1060), (760, 1120), (960, 1330)), prog(t, T_LIAB, 0.45), col=RED, width=22)
    slam(c, "LIABILITY", 760, 860, 92, t, T_LIAB, col=WHITE, bg=RED, rot=-6)


@shot(T_S3 - 0.1, T_TAKE - 0.15, theme="red", trans="whip",
      sfx=[(T_HELL, "pow", 1.2), (T_HELL, "thunder", 1.0)])
def s_hell(c, t, lt):
    cam(c, t, lt, 1.6, 1.0, 1.05, shakes=[(T_HELL, 22)])
    if t > T_HELL - 0.1:
        speed_lines(c, t, 540, 1150, alpha=0.25)
    hero(c, "shocked" if t > T_HELL else "crossed", 280, 1720, t, s=0.9, born=T_HELL if t > T_HELL else None)
    cast(c, "bad_wife", 790, 1720, t, s=1.0, flip=True)
    if t > T_HELL - 0.1:
        flames(c, 540, 1800, 1200, t, h=300 * ease_out(prog(t, T_HELL - 0.1, 0.4)))
    speech_bubble(c, 720, 720, 420, 230, t)
    impact(c, 300, 820, t, T_HELL, label="HELL!", col="#E74C3C", size=170, dur=1.2, txt_col=WHITE)
    flash(c, t, T_HELL)


@shot(T_TAKE - 0.15, T_NOTEVEN - 0.1, theme="red", trans="whip",
      sfx=[(T_TAKE + 0.1, "swish", 1.0), (T_TAKE + 0.4, "register", 1.0), (T_TAKE + 0.7, "gasp", 0.9)])
def s_take(c, t, lt):
    cam(c, t, lt, 2, 1.0, 1.04)
    k = ease_io(prog(t, T_TAKE + 0.1, 0.6))
    hero(c, "shocked" if k > 0.5 else "crossed", 270, 1720, t, s=0.95, born=T_TAKE + 0.4 if k > 0.5 else None)
    if k < 1:
        cast(c, "bad_wife_smug", 810, 1720, t, s=1.0)
        bx = 400 + (700 - 400) * k
        by = 1300 - 200 * math.sin(math.pi * k)
        with xf(c, bx, by, rot=360 * k):
            money_bag(c, 0, 0, 0.9)
    else:
        cast(c, "bad_wife_money", 810, 1720, t, s=1.0, born=T_TAKE + 0.7)
        burst_particles(c, 810, 1300, t, T_TAKE + 0.7, cols=("#7CC47F", "#F5C542"))


@shot(T_NOTEVEN - 0.1, T_S3c - 0.1, theme="grey", trans="whip",
      sfx=[(T_NOTEVEN + 0.3, "thunder", 1.0), (T_NOTEVEN + 0.6, "sad", 0.7)])
def s_dread(c, t, lt):
    cam(c, t, lt, 2, 1.0, 1.04)
    house(c, 700, 1450, 1.3, "bad", t)
    storm_cloud(c, 700, 760, 1.0, t)
    rain(c, t)
    hero(c, "rain", enter(t, T_NOTEVEN, 20, 260, 1.8), 1740, t, s=0.9, hop=6)


@shot(T_S3c - 0.1, L(4) - 0.05, theme="red", trans="whip",
      sfx=[(T_DIV, "pow", 1.2), (T_DIV + 0.35, "stamp", 1.0), (at("half", T_DIV), "swish", 1.0),
           (at("half", T_DIV) + 0.3, "register", 1.0), (at("alimony", T_DIV), "pow", 0.8),
           (at("child", T_DIV), "pow", 0.8), (at("support", T_DIV) + 0.3, "slide_down", 1.0)])
def s_divorce(c, t, lt):
    th = at("half", T_DIV)
    tsup = at("support", T_DIV)
    cam(c, t, lt, 7, 1.0, 1.04, shakes=[(T_DIV, 14), (th, 10)])
    k = ease_io(prog(t, th, 0.7))
    pose = "cry" if t > tsup + 0.3 else ("shocked" if t > th else "crossed")
    hero(c, pose, 190, 1750, t, s=0.8, born={"cry": tsup + 0.3, "shocked": th}.get(pose))
    cast(c, "bad_wife_money" if t > th else "bad_wife_smug", 890, 1750, t, s=0.85, born=th if t > th else None)
    cash_stack(c, 500 - 40 * k, 1690, 1.0, 6)
    with xf(c, 580 + 220 * k, 1690 - 140 * math.sin(math.pi * k)):
        cash_stack(c, 0, 0, 1.0, 6)
    if t > th - 0.2 and k < 1:
        setc(c, RED); c.set_line_width(8); c.set_dash([24, 16])
        c.move_to(540, 1380); c.line_to(540, 1750); c.stroke(); c.set_dash([])
    p = pop(t, T_DIV, 0.35)
    if p:
        with xf(c, 540, 760, s=p, rot=-4):
            paper(c, 0, 0, "DIVORCE", 1.15, size=44)
        impact(c, 640, 860, t, T_DIV + 0.35, label="FILED", col="#E74C3C", size=110, dur=99, txt_col=WHITE)
    for (tt, lab, x, rot) in ((at("alimony", T_DIV), "ALIMONY", 230, -12),
                              (at("child", T_DIV), "CHILD\nSUPPORT", 850, 12)):
        q = pop(t, tt, 0.35)
        if q:
            with xf(c, x, 1080, s=q * 0.75, rot=rot + 4 * math.sin(t * 3)):
                rrect(c, -150, -90, 300, 180, 14); fs(c, hexc("#7CC47F"))
                for i, part in enumerate(lab.split("\n")):
                    text(c, part, 0, -10 + i * 48 - (20 if "\n" in lab else -10), 44, hexc("#1E4D2B"))
    soul(c, 190, 1360, t, tsup + 0.3, s=0.9)


# ================================================================== 4. eyes open
T_EYES = at("eyes", L(4))


@shot(L(4) - 0.05, L(5) - 0.05, theme="blue", trans="flip",
      sfx=[(at("patience", L(4)), "boing", 0.8), (at("knowledge", L(4)), "boing", 0.8), (T_EYES, "ding", 1.0),
           (T_EYES, "twinkle", 0.8)])
def s_eyes_open(c, t, lt):
    cam(c, t, lt, 4, 1.0, 1.05)
    hero(c, "thumbs" if t > T_EYES else "crossed", 540, 1780, t, born=T_EYES if t > T_EYES else L(4))
    for (word, x, y, fn) in (("patience", 220, 860, lambda: hourglass(c, 0, 0, 1.0, t)),
                             ("knowledge", 540, 720, lambda: book(c, 0, 0, 0.9, "#3B6FD1", "")),
                             ("eyes", 860, 860, lambda: eye_icon(c, 0, 0, 0.9, t))):
        tt = at(word, L(4))
        q = pop(t, tt, 0.35)
        if q:
            with xf(c, x, y, s=q):
                fn()
            scribble_circle(c, x, y, 150, 150, prog(t, tt + 0.15, 0.4), col=RED, width=9)


# ================================================================== 5. ideals
T_THEY = at("They", L(5))
T_PROB = at("The", at("of", at("approves", L(5))))
T_IDEALS = at("ideals", L(5))


@shot(L(5) - 0.05, T_THEY - 0.1, theme="purple", trans="whip",
      sfx=[(T_IDEALS, "harp", 1.0), (T_IDEALS + 0.1, "twinkle", 0.8)])
def s_young_men(c, t, lt):
    cam(c, t, lt, 3, 1.0, 1.05)
    for i, x in enumerate((190, 540, 890)):
        q = pop(t, T_IDEALS + i * 0.12, 0.4)
        if q:
            thought_cloud(c, x, 1010, 300, 330, from_xy=(x, 1230), scale=q * 0.95)
            with xf(c, x, 1010, s=q):
                gold_person(c, 0, 140, s=0.38, t=t)
    cast(c, "guy_1", 190, 1760, t, s=0.85, born=L(5))
    hero(c, "love", 540, 1760, t, s=0.82, born=L(5) + 0.15)
    cast(c, "guy_2", 890, 1760, t, s=0.85, born=L(5) + 0.3)


@shot(T_THEY - 0.1, T_PROB - 0.1, theme="purple", trans="cut",
      sfx=[(at("opinions", T_THEY), "pop", 1.0), (at("logically", T_THEY), "pop", 1.0),
           (at("approves", T_THEY), "pop", 1.0)])
def s_ideal_list(c, t, lt):
    cam(c, t, lt, 7, 1.0, 1.04)
    q = pop(t, T_THEY, 0.4)
    light_rays(c, 560, 700, t, "#FFE680", alpha=0.3 * q, r=520)
    thought_cloud(c, 560, 700, 640, 560, from_xy=(300, 1180), scale=q)
    if q:
        with xf(c, 560, 700, s=q):
            gold_person(c, 0, 230, s=0.62, t=t)
    hero(c, "love", 210, 1780, t, s=0.85)
    for i, (word, lab) in enumerate((("opinions", "Agrees with me"), ("logically", "Always logical"),
                                     ("approves", "Acts how I like"))):
        tt = at(word, T_THEY)
        y = 1170 + i * 175
        slam(c, lab, 690, y, 50, t, tt, col=INK, bg=WHITE, rot=(-2, 2, -1)[i])
        checkmark(c, 1000, y, 0.6, pop(t, tt + 0.15, 0.3))


@shot(T_PROB - 0.1, L(6) - 0.15, theme="purple", trans="cut",
      sfx=[(at("not", T_PROB), "record_scratch", 1.0), (at("exist", T_PROB) + 0.1, "poof", 1.2),
           (at("fool", T_PROB), "slide_down", 1.0), (at("fool", T_PROB) + 0.1, "pow", 0.9)])
def s_fool(c, t, lt):
    te = at("exist", T_PROB) + 0.1
    tf = at("fool", T_PROB)
    cam(c, t, lt, 6, 1.0, 1.05, punches=[(te, 0.2, (540, 1250)), (tf, 0.15, (540, 1300))])
    pose = "facepalm" if t > tf else ("shocked" if t > te else "love")
    hero(c, pose, 540, 1780, t, born={"facepalm": tf, "shocked": te}.get(pose))
    if t < te:
        thought_cloud(c, 560, 640, 560, 500, from_xy=(560, 1050))
        with xf(c, 560, 640):
            gold_person(c, 0, 200, s=0.54, t=t)
        big_x(c, 560, 640, 160, prog(t, at("not", T_PROB), 0.25))
    puff(c, 560, 640, prog(t, te, 0.7), r=240)
    impact(c, 790, 820, t, tf + 0.1, label="FOOL", col="#F5C542", size=170, dur=99)


# ================================================================== 6. repeat after me
T6 = [at("ideals", L(6) - 0.5)]
T6.append(at("ideals", at("matter", L(6) - 0.5)))
T6.append(at("real", L(6)))
T6.append(at("real", at("and", at("options", L(6)))))


@shot(L(6) - 0.15, L(7) - 0.05, theme="cream", trans="iris",
      sfx=[(tt, "pow", 1.0) for tt in T6])
def s_chant(c, t, lt):
    cam(c, t, lt, 9, 1.0, 1.03, focus=(540, 960),
        punches=[(tt, 0.06) for tt in T6], shakes=[(tt, 12) for tt in T6])
    speed_lines(c, t, 540, 960, n=30, alpha=0.12, inner=520)
    hero(c, "flex", 540, 1900, t, s=0.78, born=L(6))
    text(c, "Repeat after me:", 540, 470, 58, DARKRED, bold=False, outline=(WHITE, 8))
    slam(c, "IDEALS DO NOT MATTER", 540, 640, 64, t, T6[0], bg=WHITE, rot=-2)
    slam(c, "IDEALS DO NOT EXIST", 540, 830, 64, t, T6[1], bg=WHITE, rot=2)
    slam(c, "REAL WORLD OPTIONS", 540, 1030, 64, t, T6[2], col=WHITE, bg=GREEN, rot=-2)
    slam(c, "+ REAL WORLD CONSEQUENCES", 540, 1210, 52, t, T6[3], col=WHITE, bg=GREEN, rot=1)
    underline(c, 330, 750, 1095, prog(t, T6[2] + 0.4, 0.4), col=GOLD, width=10)


# ================================================================== 7. comparing
T_FALLS = at("falls", L(7))
T_EX7 = at("exist", L(7))


@shot(L(7) - 0.05, L(8) - 0.05, theme="pink", trans="whip",
      sfx=[(T_FALLS, "buzzer", 0.7), (T_FALLS + 0.2, "buzzer", 0.5), (T_FALLS + 0.4, "buzzer", 0.5),
           (T_EX7, "poof", 1.2)])
def s_compare(c, t, lt):
    cam(c, t, lt, 8, 1.0, 1.04)
    if t < T_EX7 + 0.1:
        thought_cloud(c, 560, 720, 520, 540, from_xy=(240, 1250))
        with xf(c, 560, 720):
            gold_person(c, 0, 220, s=0.54, t=t)
    puff(c, 560, 720, prog(t, T_EX7 + 0.1, 0.7), r=230)
    hero(c, "shocked" if t > T_EX7 else "search", 160, 1790, t, s=0.75, born=T_EX7 if t > T_EX7 else None)
    for i, (pose, x) in enumerate((("woman_a", 430), ("woman_b", 670), ("woman_c", 910))):
        cast(c, pose, x, 1790, t, s=0.78, born=at("every", L(7)) + 0.25 * i)
        x_badge(c, x, 1790 - 0.78 * CAST_H - 60, 0.8, pop(t, T_FALLS + 0.2 * i, 0.3))


# ================================================================== 8-9. too many ANDs
ITEMS = [("virgin", "Virgin"), ("cook", "Can cook"), ("feminine", "Feminine"), ("young", "Young"),
         ("beautiful", "Beautiful"), ("family", "Powerful family"), ("children", "Wants children"), ("tall", "Tall"),
         ("devotion", "100% devotion"), ("dreams", "Sacrifices her dreams"), ("libido", "High libido"),
         ("smoke", "No smoking or drinking"), ("iq", "Very high IQ"), ("money", "Makes a lot of money"),
         ("frugal", "Frugal"), ("logical", "Logical, not emotional")]
_t = L(8)
ITEM_T = []
for _w, _lab in ITEMS:
    _t = at(_w, _t)
    ITEM_T.append(_t)
T_TOOMANY = at("many", L(9))


@shot(L(8) - 0.05, L(10) - 0.05, theme="cream", trans="whip",
      sfx=[(tt - 0.3, "pop", 0.9) for tt in ITEM_T] +
          [(T_TOOMANY - 0.1, "pow", 1.4), (T_TOOMANY, "buzzer", 0.9), (T_TOOMANY + 0.1, "ooh", 0.8)])
def s_ands(c, t, lt):
    cam(c, t, lt, 18, 1.0, 1.03, focus=(540, 1000), shakes=[(T_TOOMANY - 0.1, 20)],
        punches=[(T_TOOMANY - 0.1, 0.08)])
    if t > T_TOOMANY - 0.1:
        speed_lines(c, t, 540, 1050, alpha=0.3)
    top = 330
    rrect(c, 110 + 12, top + 12, 860, 1430, 18); setc(c, INK); c.fill()
    rrect(c, 110, top, 860, 1430, 18); fs(c, WHITE)
    text(c, "My IDEAL Wife:", 540, top + 95, 66)
    underline(c, 290, 790, top + 125, prog(t, L(8), 0.6), col=RED, width=8)
    big = t > T_TOOMANY
    for i, ((_, lab), tt) in enumerate(zip(ITEMS, ITEM_T)):
        q = pop(t, tt - 0.3, 0.25)
        if not q:
            continue
        y = top + 200 + i * 77
        with xf(c, 170, y, s=q):
            if i:
                wob = 1 + 0.18 * math.sin(t * 14 + i) if big else 1
                with xf(c, 55, -14, s=wob, rot=(6 * math.sin(t * 9 + i) if big else 0)):
                    text(c, "AND", 0, 14, 44, RED)
            text(c, lab, 125, 0, 44, INK, bold=False, align="left")
            checkmark(c, 730, -14, 0.3)
    hero(c, "facepalm" if big else "crossed", 960, 1960, t, s=0.5, born=T_TOOMANY if big else None)
    if sum(1 for tt in ITEM_T if t > tt) > 10 and not big:
        sweat_flood(c, 960, 1800, t, s=0.5)
    impact(c, 540, 1050, t, T_TOOMANY - 0.1, label="TOO MANY ANDs!", col="#F5C542", size=330, dur=99)


# ================================================================== 10. probability zero / alone forever
T_IF10 = at("If", L(10) + 3)
T_ZERO = at("0%", L(10))
T_STAY = at("stay", T_IF10)


@shot(L(10) - 0.05, T_IF10 - 0.1, theme="grey", trans="flip",
      sfx=[(L(10) + 0.4 + i * 0.12, "tick", 0.7) for i in range(12)] +
          [(T_ZERO, "pow", 1.1), (T_ZERO + 0.05, "buzzer", 0.9), (at("exist", L(10)), "sad", 0.8)])
def s_gauge(c, t, lt):
    cam(c, t, lt, 4, 1.0, 1.04, shakes=[(T_ZERO, 18)])
    k = ease_io(prog(t, L(10) + 0.3, T_ZERO - L(10) - 0.3))
    v = 100 * (1 - k) + (3 * math.sin(t * 30) * clamp(1 - (t - T_ZERO) * 2) if t > T_ZERO else 0)
    text(c, "Chance she exists:", 540, 560, 64, outline=(WHITE, 8))
    gauge(c, 540, 1060, 1.3, max(0, v))
    impact(c, 800, 740, t, T_ZERO, label="ZERO!", col="#E74C3C", size=140, dur=1.4, txt_col=WHITE)
    if t > T_ZERO:
        hface(c, "shocked", 540, 1530, 330, t, born=T_ZERO, rot=-3)
    else:
        hface(c, "think", 540, 1530, 330, t, born=L(10), rot=-3)


@shot(T_IF10 - 0.1, L(11) - 0.05, theme="grey", trans="cut",
      sfx=[(at("perfect", T_IF10), "harp", 0.9), (T_STAY, "slide_down", 1.0), (T_STAY + 0.4, "sad", 1.0)])
def s_alone(c, t, lt):
    cam(c, t, lt, 5, 1.0, 1.06)
    light_rays(c, 540, 760, t, "#FFE680", alpha=0.35, r=600)
    with xf(c, 540, 760):
        rrect(c, -190, -260, 380, 500, 12); fs(c, GOLD)
        rrect(c, -150, -220, 300, 420, 8); fs(c, hexc("#FFF6D6"))
        c.save(); rrect(c, -150, -220, 300, 420, 8); c.clip()
        gold_person(c, 0, 270, s=0.6, t=t)
        c.restore()
    old = t > T_STAY
    if old:
        cobweb(c, 0, 330, 1.2 * pop(t, T_STAY, 0.5))
        cobweb(c, W, 330, 1.2 * pop(t, T_STAY + 0.2, 0.5), flipx=True)
        bench(c, 540, 1790)
        cast(c, "old_mentor_sit", 540, 1790, t, s=0.95, born=T_STAY)
        puff(c, 540, 1450, prog(t, T_STAY, 0.6), r=260)
        slam(c, "Still single...", 540, 1150, 56, t, T_STAY + 0.3, bg=WHITE, rot=-3)
    else:
        hero(c, "love", 540, 1790, t, s=0.9)


# ================================================================== 11. options & priorities
T_OPT = at("options", L(11))
T_PRIO = at("prioritize", L(11))
T_CONS = at("consequences", L(11))


@shot(L(11) - 0.05, L(12) - 0.15, theme="green", trans="whip",
      sfx=[(T_OPT + 0.2 * i, "boing", 0.7) for i in range(3)] + [(T_PRIO, "pow", 1.0), (T_CONS, "pop", 1.0)])
def s_options(c, t, lt):
    cam(c, t, lt, 9, 1.0, 1.04, punches=[(T_PRIO, 0.1, (540, 800))])
    hero(c, "crossed", 150, 1790, t, s=0.78)
    for i, (pose, x) in enumerate((("woman_a", 420), ("woman_b", 660), ("woman_c", 900))):
        cast(c, pose, x, 1790, t, s=0.78, born=T_OPT + 0.2 * i)
        hy = 1790 - 0.78 * CAST_H - 70
        r = pop(t, T_PRIO + 0.2 * i, 0.3)
        if r:
            with xf(c, x, hy, s=r):
                circle(c, 0, 0, 52); fs(c, hexc("#3B6FD1"))
                text(c, str(i + 1), 0, 22, 64, WHITE)
        r = pop(t, T_CONS + 0.2 * i, 0.3)
        if r:
            with xf(c, x, 1040, s=r):
                text_card(c, -50, 0, "+", 1, size=60, col=WHITE, bg=GREEN)
                text_card(c, 50, 0, "–", 1, size=60, col=WHITE, bg=RED)
    slam(c, "PRIORITIZE", 540, 620, 84, t, T_PRIO, col=WHITE, bg=hexc("#3B6FD1"), rot=-3)


# ================================================================== 12. the docile wife
T_BUT12 = at("But", L(12))
T_SOMETHING = at("Something", L(12))
T_IDEA = at("idea", L(12))


@shot(L(12) - 0.15, T_BUT12 - 0.1, theme="pink", trans="iris",
      sfx=[(at("shy", L(12)), "twinkle", 0.9), (T_IDEA, "ding", 1.0)])
def s_shy(c, t, lt):
    cam(c, t, lt, 4, 1.0, 1.05)
    cast(c, "shy", 340, 1740, t, s=1.0, born=L(12))
    sparkles(c, 340, 1300, 260, t, n=6, col=hexc("#F7A8B8"))
    hero(c, "thumbs" if t > T_IDEA else "crossed", 790, 1740, t, s=0.92, flip=True,
         born=T_IDEA if t > T_IDEA else None)
    q = pop(t, T_IDEA, 0.35)
    if q:
        light_rays(c, 790, 820, t, "#FFE680", alpha=0.45 * q, r=380)
        lightbulb(c, 790, 830, 0.9 * q, t)


@shot(T_BUT12 - 0.1, T_SOMETHING - 0.1, theme="pink", trans="cut",
      sfx=[(at("dependent", T_BUT12), "pow", 1.0)] +
          [(at("everything", T_BUT12) + 0.18 * i, "boing", 0.7) for i in range(5)] +
          [(at("tasks", T_BUT12), "slide_down", 0.8)])
def s_dependent(c, t, lt):
    cam(c, t, lt, 6, 1.0, 1.04)
    te = at("everything", T_BUT12)
    n = 1 + sum(1 for i in range(5) if t > te + 0.18 * i)
    box_pile(c, 900, 1790, n)
    hero(c, "facepalm" if n > 3 else "crossed", 650, 1790, t, s=0.92, born=te + 0.36 if n > 3 else None)
    if n > 3:
        sweat_flood(c, 650, 1500, t, s=0.9)
    cast(c, "shy_shrug", 260, 1790, t, s=0.95)
    slam(c, "DEPENDENT", 320, 780, 64, t, at("dependent", T_BUT12), col=WHITE, bg=RED, rot=-8)
    qmarks(c, t, at("tasks", T_BUT12), ((170, 1000), (270, 940), (370, 1000)))


@shot(T_SOMETHING - 0.1, L(13) - 0.05, theme="blue", trans="whip",
      sfx=[(T_SOMETHING + 0.2, "splat", 1.0), (at("call", T_SOMETHING), "pow", 0.8),
           (at("won't", T_SOMETHING), "sad", 0.7)])
def s_sink(c, t, lt):
    tc = at("call", T_SOMETHING)
    cam(c, t, lt, 5, 1.0, 1.04, punches=[(tc, 0.12, (800, 1250))])
    sink(c, 330, 1250, 1.05, t)
    hero(c, "phone" if t > tc else "shocked", 800, 1790, t, s=0.92, flip=True, born=tc if t > tc else T_SOMETHING)
    cast(c, "shy_shrug", 280, 1840, t, s=0.72)
    slam(c, "Call the repairman!", 760, 760, 54, t, tc, bg=WHITE, rot=3)


# ================================================================== 13. what you can never have
T_NEVER = at("never", L(13))


@shot(L(13) - 0.05, L(14) - 0.05, theme="grey", trans="splat",
      sfx=[(L(13) + 0.1, "dun", 1.0), (T_NEVER, "pow", 1.2)])
def s_never(c, t, lt):
    cam(c, t, lt, 2, 1.0, 1.05, shakes=[(T_NEVER, 22)])
    slam(c, "You can NEVER have:", 540, 620, 68, t, L(13), bg=WHITE, rot=-2)
    q = pop(t, T_NEVER, 0.35)
    if q:
        speed_lines(c, t, 540, 1080, alpha=0.25)
        padlock(c, 540, 1050, 1.6 * q)
    hero(c, "shocked" if t > T_NEVER else "crossed", 540, 1900, t, s=0.6, born=T_NEVER if t > T_NEVER else None)


# ================================================================== 14. #1 mating strategy
T_ALL14 = at("all", L(14))


@shot(L(14) - 0.05, L(15) - 0.05, theme="purple", trans="whip",
      sfx=[(L(14), "pow", 0.8), (at("female", L(14)), "dun", 0.9)] +
          [(T_ALL14 + 0.15 * i, "boing", 0.7) for i in range(3)] + [(T_ALL14 + 0.5, "ooh", 0.9)])
def s_strategy(c, t, lt):
    cam(c, t, lt, 6, 1.0, 1.04)
    slam(c, "#1", 140, 470, 80, t, L(14) - 0.05, col=WHITE, bg=RED)
    slam(c, "Female mating strategy", 600, 470, 50, t, at("female", L(14)), bg=WHITE)
    light_rays(c, 840, 900, t, "#FFE680", alpha=0.35, r=520)
    # three men on rising steps, Chad on top
    with xf(c, 600, 1360):
        for i in range(3):
            rrect(c, -330 + i * 220, -i * 120 - 120, 220, i * 120 + 120, 6); fs(c, hexc("#E2D6B8"))
    cast(c, "guy_2", 380, 1240, t, s=0.42)
    cast(c, "guy_1", 600, 1120, t, s=0.42)
    cast(c, "chad", 820, 1000, t, s=0.48)
    for i, (pose, x) in enumerate((("woman_a", 160), ("woman_b", 390), ("woman_c", 620), ("shy", 860))):
        bt = L(14) if i == 0 else T_ALL14 + 0.15 * (i - 1)
        cast(c, pose, x, 1900, t, s=0.55, born=bt)
        if t > bt + 0.3:
            heart(c, x + 30, 1450 + 8 * math.sin(t * 4 + i), 0.45)
    heart_burst(c, 820, 800, t, T_ALL14 + 0.5, n=12, r=300)


# ================================================================== 15. #2 unconditional love
T_ALL15 = at("all", L(15))


@shot(L(15) - 0.05, T_ALL15 - 0.1, theme="pink", trans="whip",
      sfx=[(L(15), "pow", 0.8), (at("mother", L(15)), "harp", 0.9)])
def s_mom(c, t, lt):
    cam(c, t, lt, 2.5, 1.0, 1.05)
    slam(c, "#2", 140, 470, 80, t, L(15) - 0.05, col=WHITE, bg=RED)
    slam(c, "Unconditional love", 600, 470, 52, t, L(15) + 0.2, bg=WHITE)
    cast(c, "mom", 420, 1760, t, s=1.05, born=L(15))
    hero(c, "love", 800, 1760, t, s=0.8, flip=True)
    floating_hearts(c, 600, 1100, lt, 5, 160)


@shot(T_ALL15 - 0.1, L(16) - 0.05, theme="red", trans="cut",
      sfx=[(at("conditional", T_ALL15), "pow", 1.1), (at("nag", T_ALL15), "buzzer", 0.8),
           (at("leave", T_ALL15), "swish", 1.0), (at("leave", T_ALL15) + 0.5, "sad", 0.9)])
def s_conditional(c, t, lt):
    cam(c, t, lt, 9, 1.0, 1.04)
    tc = at("conditional", T_ALL15)
    tm = at("meet", T_ALL15)
    tn = at("nag", T_ALL15)
    tl = at("leave", T_ALL15)
    k = clamp((t - tm) / max(0.5, tn - tm))
    with xf(c, 300, 820, s=1 + 0.05 * math.sin(t * 6) * (1 - k)):
        heart(c, 0, 0, 2.2, "#F2D7D5")
        c.save(); c.rectangle(-300, -300 + 400 * k * 0.55, 600, 600); c.clip()
        heart(c, 0, 0, 2.2)
        c.restore()
    slam(c, "*CONDITIONS APPLY", 640, 740, 54, t, tc, col=RED, bg=WHITE, rot=-6)
    if t < tn - 0.2:
        cast(c, "woman_a", 330, 1780, t, s=1.0)
    elif t < tl:
        cast(c, "woman_a_nag", 360, 1780, t, s=1.0, born=tn - 0.2)
        speech_bubble(c, 420, 1050, 360, 200, t, tail=(-40, 130))
    else:
        cast(c, "woman_a_leave", enter(t, tl, 330, -350, 1.3), 1780, t, s=1.0, hop=8)
    pose = "cry" if t > tl + 0.2 else ("crossed")
    hero(c, pose, 820, 1780, t, s=0.92, flip=True, born=tl + 0.2 if pose == "cry" else None)


# ================================================================== 16. #3 logic over emotion
T_MORE = at("More", L(16))
T_RARE = at("rare", L(16))


@shot(L(16) - 0.05, T_MORE - 0.1, theme="blue", trans="whip",
      sfx=[(L(16), "pow", 0.8), (at("Ayn", L(16)), "boing", 0.9), (T_RARE, "pow", 1.0), (T_RARE + 0.1, "harp", 0.9)])
def s_logic(c, t, lt):
    cam(c, t, lt, 5.5, 1.0, 1.05)
    slam(c, "#3", 140, 470, 80, t, L(16) - 0.05, col=WHITE, bg=RED)
    slam(c, "Logic over emotion", 600, 470, 52, t, L(16) + 0.2, bg=WHITE)
    ta = at("Ayn", L(16))
    if t > T_RARE:
        light_rays(c, 400, 1300, t, "#C7AEEB", alpha=0.45, r=700)
    cast(c, "smart", 400, 1790, t, s=1.05, born=ta)
    if t > ta:
        slam(c, "AYN RAND", 400, 980, 44, t, ta + 0.2, col=WHITE, bg=hexc("#2C3E50"), rot=-4)
    impact(c, 800, 1000, t, T_RARE, label="RARE", col="#C7AEEB", size=170, dur=99, txt_col=hexc("#5B2C8F"))
    if t > T_RARE:
        sparkles(c, 400, 1300, 320, t, n=8)


@shot(T_MORE - 0.1, L(17) - 0.05, theme="red", trans="cut",
      sfx=[(at("99", T_MORE) + i * 0.1, "tick", 0.6) for i in range(12)] +
          [(at("women", T_MORE) + 0.3, "pow", 1.0), (at("behave", T_MORE), "boing", 0.8)])
def s_emotion(c, t, lt):
    t9 = at("99", T_MORE)
    cam(c, t, lt, 8, 1.0, 1.04, shakes=[(at("women", T_MORE) + 0.3, 12)])
    k = ease_out(prog(t, t9, 1.3))
    q = pop(t, t9 - 0.15, 0.3)
    if q:
        with xf(c, 540, 700, s=q * (1 + 0.04 * math.sin(t * 8))):
            text(c, f"{99.99 * k:.2f}%", 0, 0, 190, RED, outline=(INK, 10))
        text(c, "of women value", 540, 840, 60, INK, bold=False, outline=(WHITE, 8))
    slam(c, "EMOTION > LOGIC", 540, 980, 64, t, at("emotion", T_MORE), col=WHITE, bg=RED)
    tb = at("behave", T_MORE)
    crowd = (("woman_a", 130), ("woman_b", 330), ("shy", 530), ("woman_c", 740), ("bad_wife", 950))
    for i, (pose, x) in enumerate(crowd):
        cast(c, pose, x, 1880, t, s=0.62, born=at("women", T_MORE) + 0.12 * i, flip=i == 4)
        if t > tb:
            r = pop(t, tb + 0.1 * i, 0.3)
            with xf(c, x, 1340, s=r):
                if i % 2 == 0:
                    heart(c, 0, 0, 0.6)
                else:
                    storm_cloud(c, 0, 0, 0.35, t, bolt=True)


# ================================================================== 17. can find vs can't
T_BUT17 = at("But", L(17))
T_YOU17 = at("you", at("strategy", T_BUT17))


@shot(L(17) - 0.05, T_BUT17 - 0.1, theme="green", trans="whip",
      sfx=[(at(w, L(17)), "boing", 0.8) for w in ("intelligent", "tall", "powerful")] +
          [(at(w, L(17)) + 0.2, "ding", 0.6) for w in ("intelligent", "tall", "powerful")])
def s_can_find(c, t, lt):
    cam(c, t, lt, 5, 1.0, 1.04)
    slam(c, "You CAN find:", 540, 470, 64, t, L(17), col=WHITE, bg=GREEN)
    for i, (word, pose, x, sc) in enumerate((("intelligent", "smart", 190, 0.8), ("tall", "woman_c", 540, 1.0),
                                            ("powerful", "woman_b", 890, 0.8))):
        tt = at(word, L(17))
        cast(c, pose, x, 1810, t, s=sc, born=tt)
        top = 1810 - sc * CAST_H
        if pose == "woman_b" and t > tt:
            crown(c, x - 5, top + 40, 0.9 * pop(t, tt + 0.2, 0.3))
        checkmark(c, x, top - 90, 0.85, pop(t, tt + 0.2, 0.3))


@shot(T_BUT17 - 0.1, T_YOU17 - 0.1, theme="red", trans="whip",
      sfx=[(at(w, T_BUT17) + 0.35, "buzzer", 0.6) for w in ("reasons", "unconditionally", "follow")])
def s_cant_find(c, t, lt):
    cam(c, t, lt, 6, 1.0, 1.04)
    slam(c, "But NOT:", 540, 470, 64, t, T_BUT17, col=WHITE, bg=RED)
    for i, (w, lab) in enumerate((("reasons", "Reasons like a man"), ("unconditionally", "Loves unconditionally"),
                                  ("follow", "No mating strategy"))):
        tt = at(w, T_BUT17)
        y = 700 + i * 220
        slam(c, lab, 470, y, 54, t, tt - 0.2, bg=WHITE, rot=(-2, 2, -1)[i])
        x_badge(c, 950, y, 0.9, pop(t, tt + 0.35, 0.3))
    hero(c, "shrug", 540, 1900, t, s=0.66, born=T_BUT17)


@shot(T_YOU17 - 0.1, L(18) - 0.05, theme="grey", trans="whip",
      sfx=[(at("rest", T_YOU17), "sad", 1.0)])
def s_forever(c, t, lt):
    cam(c, t, lt, 2.5, 1.0, 1.05)
    cobweb(c, 0, 330, 1.2)
    cobweb(c, W, 330, 1.2, flipx=True)
    cast(c, "old_mentor_search", enter(t, T_YOU17, 180, 520, 2.5), 1790, t, s=1.05, hop=4)
    slam(c, "...still looking", 540, 700, 60, t, at("rest", T_YOU17), bg=WHITE, rot=-3)


# ================================================================== 18. accept reality
T_BUT18 = at("but", L(18))
T_MAKE = at("Make", L(18))
T_CHOICE = at("choice", T_MAKE)


@shot(L(18) - 0.05, T_BUT18 - 0.1, theme="grey", trans="iris", sfx=[(L(18) + 0.2, "sad", 0.7)])
def s_painful(c, t, lt):
    cam(c, t, lt, 2.5, 1.0, 1.12, focus=(540, 1400))
    rain(c, t, n=30, seed=5)
    hero(c, "cry", 540, 1780, t, s=1.15, born=L(18))


@shot(T_BUT18 - 0.1, T_MAKE - 0.1, theme="green", trans="whip",
      sfx=[(at("matter", T_BUT18) + 0.1, "poof", 1.2)] +
          [(at("options", T_BUT18) + 0.2 * i, "boing", 0.8) for i in range(3)])
def s_real_options(c, t, lt):
    cam(c, t, lt, 3, 1.0, 1.04)
    tm = at("matter", T_BUT18) + 0.1
    if t < tm:
        thought_cloud(c, 540, 800, 520, 540)
        with xf(c, 540, 800):
            gold_person(c, 0, 220, s=0.54, t=t)
        big_x(c, 540, 800, 160, prog(t, tm - 0.4, 0.25))
    puff(c, 540, 800, prog(t, tm, 0.7), r=240)
    to = at("options", T_BUT18)
    for i, (pose, x) in enumerate((("woman_a", 190), ("woman_b", 540), ("woman_c", 890))):
        cast(c, pose, x, 1810, t, s=0.85, born=to + 0.2 * i)


@shot(T_MAKE - 0.1, L(19) - 0.05, theme="gold", trans="whip",
      sfx=[(T_CHOICE, "harp", 1.0), (T_CHOICE + 0.1, "cheer", 1.0)])
def s_choose(c, t, lt):
    cam(c, t, lt, 3.3, 1.0, 1.06, punches=[(T_CHOICE, 0.1, (560, 1300))])
    if t > T_CHOICE:
        light_rays(c, 560, 1250, t, "#FFE680", alpha=0.5, r=1000)
    hero(c, "propose" if t > T_CHOICE - 0.3 else "walk", 360, 1790, t, s=1.0, born=T_CHOICE - 0.3 if t > T_CHOICE - 0.3 else None)
    cast(c, "woman_c", 790, 1790, t, s=1.0, born=T_MAKE)
    heart_burst(c, 580, 1100, t, T_CHOICE, n=16, r=460)
    confetti(c, t, T_CHOICE, n=60, seed=4)


# ================================================================== 19. the book
BOOK = cairo.ImageSurface.create_from_png(os.path.join(HERE, "..", "assets", "book_cover.png"))
T_LINK = at("link", L(19))


def book_cover(c, x, y, s, t, rot=0.0):
    w, h = BOOK.get_width(), BOOK.get_height()
    with xf(c, x, y, s=s, rot=rot):
        rrect(c, -w / 2 + 22, -h / 2 + 26, w, h, 10); setc(c, INK[:3] + (0.85,)); c.fill()
        c.save()
        rrect(c, -w / 2, -h / 2, w, h, 10); c.clip()
        c.set_source_surface(BOOK, -w / 2, -h / 2); c.paint()
        k = (t * 0.45) % 1.6 - 0.3  # moving shine
        sx = -w / 2 + w * k * 1.6
        g = cairo.LinearGradient(sx - 120, -h / 2, sx + 120, h / 2)
        g.add_color_stop_rgba(0, 1, 1, 1, 0)
        g.add_color_stop_rgba(0.5, 1, 1, 1, 0.35)
        g.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.set_source(g); c.paint()
        c.restore()
        rrect(c, -w / 2, -h / 2, w, h, 10); fs(c, None, 8)


def down_arrow(c, x, y, s, col=DARKRED):
    with xf(c, x, y, s=s):
        poly(c, [(-30, -150), (30, -150), (30, 20), (85, 20), (0, 130), (-85, 20), (-30, 20)])
        fs(c, col)


@shot(L(19) - 0.05, L(20) - 0.05, theme="gold", trans="splat",
      sfx=[(L(19) + 0.2, "pow", 1.1), (L(19) + 0.3, "harp", 1.0), (T_LINK, "pop", 1.0),
           (at("bio", L(19)), "ding", 1.0)])
def s_book(c, t, lt):
    cam(c, t, lt, 8.5, 1.0, 1.04, focus=(540, 1000))
    q = pop(t, L(19) + 0.2, 0.45)
    if q:
        light_rays(c, 600, 880, t, "#FFD970", alpha=0.6 * q, r=1200)
        book_cover(c, 620, 880 + 10 * math.sin(t * 2), 0.82 * q, t, rot=-3 + 2 * math.sin(t * 1.3))
        sparkles(c, 620, 880, 420, t, n=8)
    hero(c, "point_side", 200, 1900, t, s=0.75, born=L(19))
    slam(c, "LINK IN BIO", 640, 1460, 72, t, T_LINK, col=WHITE, bg=DARKRED, rot=-2)
    if t > T_LINK + 0.1:
        down_arrow(c, 640, 1680 + 18 * math.sin(t * 7), pop(t, T_LINK + 0.1, 0.3) * 0.9)


# ================================================================== 20. part 2 CTA
T_FOLLOW = at("Follow", L(20))
T_MISS = at("miss", L(20))


@shot(L(20) - 0.05, DURATION + 1, theme="blue", trans="whip",
      sfx=[(at("next", L(20)), "pow", 1.0), (at("look", L(20)), "pop", 1.0), (at("run", L(20)), "pop", 1.0),
           (T_FOLLOW, "boing", 1.0), (T_MISS, "ding", 1.0), (T_MISS + 0.05, "cheer", 0.8)])
def s_cta(c, t, lt):
    cam(c, t, lt, 7, 1.0, 1.03, punches=[(T_MISS, 0.08, (540, 1300))])
    slam(c, "PART 2", 540, 500, 110, t, at("next", L(20)), col=WHITE, bg=hexc("#3B6FD1"), rot=-3)
    for (word, x, good) in (("look", 290, True), ("run", 790, False)):
        q = pop(t, at(word, L(20)), 0.35)
        if q:
            with xf(c, x, 850, s=q, rot=(-3 if good else 3)):
                rrect(c, -210 + 10, -150 + 12, 420, 300, 24); setc(c, INK); c.fill()
                rrect(c, -210, -150, 420, 300, 24); fs(c, WHITE)
                (checkmark if good else x_badge)(c, 0, -50, 1.0)
                text(c, "Traits to", 0, 60, 46, INK, bold=False)
                text(c, "LOOK FOR" if good else "RUN FROM", 0, 115, 54, GREEN if good else RED)
    q = pop(t, T_FOLLOW, 0.35)
    if q:
        follow_button(c, 540, 1200, q, pressed=prog(t, T_MISS, 0.15))
        hx = enter(t, T_FOLLOW + 0.1, 1200, 800, 0.5)
        hy = 1370 - 30 * prog(t, T_MISS - 0.1, 0.1)
        hand_cursor(c, hx, hy, 1.0)
        burst_particles(c, 540, 1200, t, T_MISS, n=22, r=360)
    hero(c, "point_you", 540, 1920, t, s=0.68, born=L(20))


frame = st.frame
SFX = st.sfx
