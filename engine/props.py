"""Props: objects, icons and scenery."""
import math, random
import cairo
from core import *


# ---------------------------------------------------------------- props
def star4(c, x, y, r):
    c.move_to(x, y - r)
    for i in range(1, 8):
        ang = i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.3
        c.line_to(x + rr * math.sin(ang), y - rr * math.cos(ang))
    c.close_path()


def sparkles(c, x, y, rad, t, n=6, alpha=1.0, col=None):
    rnd = random.Random(int(x * 7 + y))
    for i in range(n):
        ph = rnd.random() * 6.28
        ang = rnd.random() * 6.28
        d = rad * (0.5 + 0.5 * rnd.random())
        sc = 0.5 + 0.5 * math.sin(t * 4 + ph)
        if sc < 0.1:
            continue
        star4(c, x + d * math.cos(ang), y + d * math.sin(ang), 22 * sc)
        setc(c, (col or hexc("#FFE680"))[:3] + (alpha,))
        c.fill_preserve()
        setc(c, INK[:3] + (alpha,))
        c.set_line_width(3)
        c.stroke()


def thought_cloud(c, x, y, w, h, from_xy=None, scale=1.0):
    with xf(c, x, y, s=scale):
        rnd = random.Random(3)
        c.new_path()
        n = 11
        for i in range(n):
            a = 2 * math.pi * i / n
            circle(c, (w / 2 - 30) * math.cos(a), (h / 2 - 30) * math.sin(a), 60 + rnd.random() * 20)
        setc(c, INK); c.set_line_width(LW * 2); c.stroke_preserve()
        setc(c, WHITE); c.fill()
        c.save(); c.scale(1, h / w); circle(c, 0, 0, w / 2 - 20); c.restore()
        setc(c, WHITE); c.fill()
    if from_xy:
        fx, fy = from_xy
        for i, r in enumerate((14, 20, 28)):
            k = (i + 1) / 4
            circle(c, fx + (x - fx) * k * 0.7, fy + (y + h * 0.45 * scale - fy) * k, r * scale)
            fs(c, WHITE, 5)


def ring_box(c, x, y, s, open_p, t):
    with xf(c, x, y, s=s):
        rrect(c, -80, -40, 160, 90, 14)
        fs(c, hexc("#C0392B"))
        lid_h = 55 * (1 - ease_out(open_p))
        if open_p < 0.5:
            rrect(c, -85, -40 - lid_h, 170, lid_h + 10, 14)
            fs(c, hexc("#E74C3C"))
        else:
            rrect(c, -80, -150, 160, 110, 14)
            fs(c, hexc("#E74C3C"))
            rrect(c, -60, -130, 120, 75, 10)
            fs(c, WHITE, 5)
            # ring
            circle(c, 0, -40, 30)
            setc(c, INK); c.set_line_width(20); c.stroke_preserve()
            setc(c, GOLD); c.set_line_width(10); c.stroke()
            poly(c, [(-18, -78), (18, -78), (0, -50)])
            fs(c, hexc("#BFF3FF"), 4)
            sparkles(c, 0, -80, 90, t, n=4)


def question_mark(c, x, y, size, t=0.0, col=INK, rot=0):
    with xf(c, x, y, rot=rot + 6 * math.sin(t * 3)):
        text(c, "?", 0, 0, size, col, outline=(WHITE, 8))


def puff(c, x, y, p, r=120):
    """smoke poof, p in 0..1"""
    if p <= 0 or p >= 1:
        return
    rnd = random.Random(int(x))
    a = 1 - p
    for i in range(9):
        ang = rnd.random() * 6.28
        d = r * ease_out(p) * (0.4 + rnd.random() * 0.6)
        circle(c, x + d * math.cos(ang), y + d * math.sin(ang), (40 + rnd.random() * 30) * (0.6 + p))
        setc(c, hexc("#D8D3C4", a)); c.fill_preserve()
        setc(c, INK[:3] + (a,)); c.set_line_width(5); c.stroke()


def big_x(c, x, y, size, p):
    if p <= 0:
        return
    with xf(c, x, y, s=back(p)):
        for sgn in (-1, 1):
            limb(c, [(-size, -size * sgn), (size, size * sgn)], 34, RED)


def magnifier(c, hx, hy, ang=-35, s=1.0):
    with xf(c, hx, hy, s=s, rot=ang):
        limb(c, [(0, 0), (0, -110)], 22, hexc("#6B4226"))
        circle(c, 0, -175, 70)
        setc(c, hexc("#CFEFFF", 0.6)); c.fill_preserve()
        setc(c, INK); c.set_line_width(LW * 2.2); c.stroke()
        circle(c, 0, -175, 70)
        setc(c, hexc("#9AA5AE")); c.set_line_width(10); c.stroke()


def arch(c, x, y, w, h, col="#E9DFC6"):
    """simple church arch/doorway outline"""
    with xf(c, x, y):
        c.move_to(-w / 2, 0); c.line_to(-w / 2, -h + w / 2)
        c.arc(0, -h + w / 2, w / 2, math.pi, 2 * math.pi)
        c.line_to(w / 2, 0)
        c.line_to(w / 2 - 50, 0); c.line_to(w / 2 - 50, -h + w / 2)
        c.arc_negative(0, -h + w / 2, w / 2 - 50, 2 * math.pi, math.pi)
        c.line_to(-w / 2 + 50, 0)
        c.close_path()
        fs(c, hexc(col))
        # little cross on top
        limb(c, [(0, -h - 10), (0, -h - 90)], 12, hexc(col))
        limb(c, [(-28, -h - 62), (28, -h - 62)], 12, hexc(col))


def confetti(c, t, t0, n=40, seed=1):
    if t < t0:
        return
    rnd = random.Random(seed)
    cols = ["#E74C3C", "#F5C542", "#3FA7A0", "#8E44AD", "#3BAA5C", "#F08A8A"]
    for i in range(n):
        x0 = rnd.random() * W
        sp = 250 + rnd.random() * 250
        y = -50 + (t - t0) * sp - rnd.random() * 500
        if y < -40 or y > H:
            continue
        x = x0 + 40 * math.sin((t - t0) * 3 + i)
        with xf(c, x, y, rot=(t - t0) * 200 + i * 40):
            rrect(c, -10, -6, 20, 12, 2)
            setc(c, hexc(rnd.choice(cols))); c.fill()


def house(c, x, y, s, mood="happy", t=0.0):
    with xf(c, x, y, s=s):
        rrect(c, -130, -200, 260, 200, 6)
        fs(c, hexc("#F3E1C2") if mood == "happy" else hexc("#B9B2A6"))
        poly(c, [(-165, -195), (0, -330), (165, -195)])
        fs(c, hexc("#D35445") if mood == "happy" else hexc("#6E6A66"))
        rrect(c, -30, -110, 60, 110, 6)
        fs(c, hexc("#8A5A3B") if mood == "happy" else hexc("#4E4A48"))
        for wx in (-85, 85):
            rrect(c, wx - 32, -160, 64, 56, 4)
            fs(c, hexc("#FFE89A") if mood == "happy" else hexc("#5C6670"))
        if mood == "bad":
            # crack
            c.move_to(60, -200); c.line_to(40, -150); c.line_to(70, -120); c.line_to(50, -70)
            setc(c, INK); c.set_line_width(5); c.stroke()


def sun(c, x, y, r, t):
    with xf(c, x, y, rot=t * 20):
        for i in range(10):
            a = i * math.pi / 5
            limb(c, [(math.cos(a) * (r + 18), math.sin(a) * (r + 18)), (math.cos(a) * (r + 52), math.sin(a) * (r + 52))], 10, GOLD)
    circle(c, x, y, r)
    fs(c, GOLD)


def storm_cloud(c, x, y, s, t, bolt=True):
    with xf(c, x, y + 6 * math.sin(t * 2), s=s):
        c.new_path()
        for (cx, cy, r) in ((-90, 10, 60), (-30, -30, 75), (50, -20, 70), (105, 15, 55), (0, 30, 60)):
            circle(c, cx, cy, r)
        setc(c, INK); c.set_line_width(LW * 2); c.stroke_preserve()
        setc(c, hexc("#6F7680")); c.fill()
        if bolt and (t * 1.7) % 1 < 0.35:
            poly(c, [(-10, 60), (35, 60), (10, 120), (45, 120), (-25, 230), (0, 140), (-35, 140)])
            fs(c, GOLD, 5)


def sign(c, x, y, label, col, direction=1, s=1.0, p=1.0):
    """arrow-shaped signboard on a post; direction -1 points left"""
    with xf(c, x, y, s=s * p):
        limb(c, [(0, 0), (0, -260)], 22, hexc("#8A5A3B"))
        with xf(c, 0, -300, sx=direction, sy=1):
            poly(c, [(-130, -50), (90, -50), (140, 0), (90, 50), (-130, 50)])
            fs(c, col)
        text(c, label, -10 * direction, -286, 46, WHITE, outline=(INK, 7))


# ---------------------------------------------------------------- more props
def heart(c, x=0, y=0, s=1.0, col="#E74C3C"):
    with xf(c, x, y, s=s):
        c.move_to(0, 40)
        c.curve_to(-90, -20, -50, -90, 0, -45)
        c.curve_to(50, -90, 90, -20, 0, 40)
        c.close_path()
        fs(c, hexc(col), 6)


def stamp_label(c, x, y, label, col, p, size=84, rot=-8):
    """rubber-stamp rectangle with text; p = pop progress (0 = hidden)"""
    if p <= 0:
        return
    with xf(c, x, y, s=p * 1.0, rot=rot):
        c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(size)
        w = c.text_extents(label).width + 70
        h = size * 1.45
        rrect(c, -w / 2, -h / 2, w, h, 16)
        setc(c, WHITE[:3] + (0.92,)); c.fill_preserve()
        setc(c, col); c.set_line_width(12); c.stroke()
        text(c, label, 0, size * 0.36, size, col)


def text_card(c, x, y, label, p, size=80, col=INK, bg=WHITE, rot=0):
    if p <= 0:
        return
    with xf(c, x, y, s=p, rot=rot):
        c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(size)
        w = c.text_extents(label).width + 60
        h = size * 1.5
        rrect(c, -w / 2 + 10, -h / 2 + 12, w, h, 18); setc(c, INK); c.fill()
        rrect(c, -w / 2, -h / 2, w, h, 18); fs(c, bg)
        text(c, label, 0, size * 0.36, size, col)


def trend_arrow(c, x, y, s, up=True, p=1.0):
    if p <= 0:
        return
    col = GREEN if up else RED
    pts = [(-150, 90), (-60, 10), (0, 50), (130, -90)] if up else [(-150, -90), (-90, -20), (-40, -50), (130, 90)]
    k = max(2, int(len(pts) * p + 0.999))
    with xf(c, x, y, s=s):
        limb(c, pts[:k], 26, col)
        if p >= 1:
            ex, ey = pts[-1]
            ang = math.atan2(ey - pts[-2][1], ex - pts[-2][0])
            with xf(c, ex, ey, rot=math.degrees(ang)):
                poly(c, [(40, 0), (-20, -40), (-20, 40)])
                fs(c, col)


def flames(c, x, y, w, t, h=160):
    n = int(w / 70)
    for i in range(n):
        fx = x - w / 2 + (i + 0.5) * w / n
        fh = h * (0.75 + 0.25 * math.sin(t * 9 + i * 1.7))
        for k, col in ((1.0, "#E74C3C"), (0.62, "#F39C12"), (0.3, "#F9E26A")):
            c.move_to(fx - 40 * k, y)
            c.curve_to(fx - 50 * k, y - fh * k * 0.5, fx - 5, y - fh * k * 0.7, fx + 6 * math.sin(t * 7 + i), y - fh * k)
            c.curve_to(fx + 10, y - fh * k * 0.6, fx + 50 * k, y - fh * k * 0.4, fx + 40 * k, y)
            c.close_path()
            fs(c, hexc(col), 5)


def money_bag(c, x, y, s=1.0, label="$"):
    with xf(c, x, y, s=s):
        c.move_to(-40, -120); c.line_to(40, -120); c.line_to(25, -90)
        c.curve_to(120, -40, 110, 60, 0, 60); c.curve_to(-110, 60, -120, -40, -25, -90); c.close_path()
        fs(c, hexc("#C9A66B"))
        limb(c, [(-30, -95), (30, -95)], 10, hexc("#8A5A3B"))
        text(c, label, 0, 30, 80, hexc("#2E7D32"))


def cash_stack(c, x, y, s=1.0, n=5):
    with xf(c, x, y, s=s):
        for i in range(n):
            rrect(c, -90, -i * 26 - 26, 180, 30, 5)
            fs(c, hexc("#7CC47F"), 5)
        text(c, "$", 0, -n * 26 + 12, 40, hexc("#1E6B2F"))


def paper(c, x, y, label, s=1.0, rot=0, col="#FFFFFF", size=40, lines=3):
    with xf(c, x, y, s=s, rot=rot):
        rrect(c, -130, -170, 260, 340, 10)
        fs(c, hexc(col))
        text(c, label, 0, -100, size, INK)
        setc(c, hexc("#B0A890")); c.set_line_width(6)
        for i in range(lines):
            c.move_to(-90, -40 + i * 45); c.line_to(90 - (i % 2) * 40, -40 + i * 45)
        c.stroke()


def briefcase(c, x, y, s=1.0):
    with xf(c, x, y, s=s):
        rrect(c, -30, -95, 60, 40, 10); fs(c, None, 9)
        rrect(c, -80, -70, 160, 110, 12); fs(c, hexc("#8A5A3B"))
        limb(c, [(-80, -20), (80, -20)], 4, hexc("#6B4226"))


def hourglass(c, x, y, s, t):
    with xf(c, x, y, s=s, rot=10 * math.sin(t * 2)):
        poly(c, [(-60, -90), (60, -90), (8, 0), (60, 90), (-60, 90), (-8, 0)]); fs(c, hexc("#DFF3FF"))
        k = (t * 0.3) % 1
        poly(c, [(-45 * (1 - k), -80 + 80 * k), (45 * (1 - k), -80 + 80 * k), (0, -5)]); setc(c, GOLD); c.fill()
        poly(c, [(-50 * k, 85 - 60 * k), (50 * k, 85 - 60 * k), (55, 85), (-55, 85)]); setc(c, GOLD); c.fill()
        for yy in (-95, 95):
            rrect(c, -80, yy - 12, 160, 24, 8); fs(c, hexc("#8A5A3B"))


def book(c, x, y, s=1.0, col="#C0392B", label="", rot=0):
    with xf(c, x, y, s=s, rot=rot):
        rrect(c, -80, -105, 160, 210, 10); fs(c, hexc(col))
        rrect(c, -80, -105, 26, 210, 6); fs(c, INK[:3] + (0.25,), 4)
        if label:
            for i, part in enumerate(label.split("\n")):
                text(c, part, 12, -20 + i * 44, 36, WHITE)


def eye_icon(c, x, y, s, t):
    with xf(c, x, y, s=s):
        c.move_to(-110, 0); c.curve_to(-50, -80, 50, -80, 110, 0); c.curve_to(50, 80, -50, 80, -110, 0); c.close_path()
        fs(c, WHITE)
        circle(c, 8 * math.sin(t * 1.5), 0, 42); fs(c, hexc("#3B6FD1"))
        circle(c, 8 * math.sin(t * 1.5), 0, 18); setc(c, INK); c.fill()


def jester_hat(c, dy=-45):
    c.save(); c.translate(0, dy)
    for sx, col in ((-1, "#E74C3C"), (1, "#F5C542")):
        c.move_to(0, -495); c.curve_to(sx * 60, -600, sx * 140, -600, sx * 170, -540)
        c.curve_to(sx * 120, -545, sx * 90, -520, sx * 80, -480); c.close_path()
        fs(c, hexc(col))
        circle(c, sx * 172, -538, 20); fs(c, GOLD, 5)
    rrect(c, -100, -505, 200, 40, 14); fs(c, hexc("#8E44AD"))
    c.restore()


def crown(c, x=0, y=-560, s=1.0):
    with xf(c, x, y, s=s):
        poly(c, [(-70, 0), (-80, -80), (-35, -40), (0, -95), (35, -40), (80, -80), (70, 0)])
        fs(c, GOLD)
        for cx in (-35, 0, 35):
            circle(c, cx, -18, 9); fs(c, hexc("#E74C3C"), 4)


def checkmark(c, x, y, s, p=1.0, col=None):
    if p <= 0:
        return
    with xf(c, x, y, s=s * p):
        circle(c, 0, 0, 60); fs(c, col or GREEN)
        limb(c, [(-28, 2), (-6, 26), (32, -24)], 14, WHITE)


def x_badge(c, x, y, s, p=1.0):
    if p <= 0:
        return
    with xf(c, x, y, s=s * p):
        circle(c, 0, 0, 60); fs(c, RED)
        for sg in (-1, 1):
            limb(c, [(-24, -24 * sg), (24, 24 * sg)], 14, WHITE)


def gauge(c, x, y, s, value):
    """semicircle meter 0..100 %, needle at value"""
    with xf(c, x, y, s=s):
        for i, col in enumerate(("#E74C3C", "#F39C12", "#F5C542", "#3BAA5C")):
            a0 = math.pi + i * math.pi / 4
            c.move_to(0, 0); c.arc(0, 0, 300, a0, a0 + math.pi / 4); c.close_path()
            fs(c, hexc(col))
        c.move_to(0, 0); c.arc(0, 0, 150, math.pi, 2 * math.pi); c.close_path(); fs(c, CREAM)
        a = math.pi + math.pi * clamp(value / 100)
        limb(c, [(0, 0), (260 * math.cos(a), 260 * math.sin(a))], 16, INK)
        circle(c, 0, 0, 30); fs(c, INK)
        text(c, f"{value:.0f}%", 0, 140, 110, RED if value < 10 else INK)


def cobweb(c, x, y, s, flipx=False):
    with xf(c, x, y, sx=-s if flipx else s, sy=s):
        setc(c, hexc("#8C8C8C")); c.set_line_width(3)
        for i in range(6):
            a = i * math.pi / 10
            c.move_to(0, 0); c.line_to(220 * math.cos(a), 220 * math.sin(a))
        for r in (60, 110, 160, 210):
            c.move_to(r, 0)
            for i in range(1, 6):
                a = i * math.pi / 10
                c.line_to(r * math.cos(a), r * math.sin(a))
        c.stroke()


def cane(c, h):
    limb(c, [(h[0], h[1]), (h[0] + 5, h[1] + 230)], 14, hexc("#8A5A3B"))
    c.new_path(); c.arc(h[0] - 25, h[1], 25, math.pi, 2 * math.pi)
    setc(c, INK); c.set_line_width(28); c.stroke_preserve(); setc(c, hexc("#8A5A3B")); c.set_line_width(14); c.stroke()


def lightbulb(c, x, y, s, t):
    with xf(c, x, y, s=s):
        for i in range(8):
            a = i * math.pi / 4 + t
            limb(c, [(110 * math.cos(a), 110 * math.sin(a) - 20), (140 * math.cos(a), 140 * math.sin(a) - 20)], 8, GOLD)
        circle(c, 0, -20, 75); fs(c, hexc("#FFF2A8"))
        rrect(c, -35, 50, 70, 50, 8); fs(c, hexc("#9AA5AE"))


def sink(c, x, y, s, t, broken=True):
    with xf(c, x, y, s=s):
        rrect(c, -170, -40, 340, 220, 14); fs(c, hexc("#C9D6DF"))
        rrect(c, -210, -70, 420, 40, 10); fs(c, hexc("#E7EEF2"))
        limb(c, [(0, -70), (0, -200), (80, -200), (80, -170)], 22, hexc("#9AA5AE"))
        if broken:
            rnd = random.Random(5)
            for i in range(16):
                k = ((t * 1.6) + i / 16) % 1
                a = -math.pi / 2 + (rnd.random() - 0.5) * 2.2
                d = 320 * k
                circle(c, 80 + d * math.cos(a), -210 + d * math.sin(a) + 300 * k * k, 14 * (1 - k * 0.5))
                fs(c, hexc("#5DADE2"), 4)


def phone(c, h, rot=-20):
    with xf(c, h[0], h[1] - 30, rot=rot):
        rrect(c, -28, -60, 56, 110, 10); fs(c, hexc("#2B2B33"))
        rrect(c, -20, -50, 40, 80, 4); fs(c, hexc("#86D3F5"), 3)


def suitcase(c, h):
    with xf(c, h[0], h[1] + 70):
        rrect(c, -25, -85, 50, 30, 8); fs(c, None, 8)
        rrect(c, -70, -65, 140, 120, 12); fs(c, hexc("#C0392B"))


def speech_bubble(c, x, y, w, h, t, scribble=True, tail=(-60, 120), content=None):
    with xf(c, x, y):
        rrect(c, -w / 2, -h / 2, w, h, 50)
        c.move_to(-30, h / 2 - 2); c.line_to(tail[0], tail[1]); c.line_to(30, h / 2 - 2)
        fs(c, WHITE)
        rrect(c, -w / 2 + 6, -h / 2 + 6, w - 12, h - 12, 46); setc(c, WHITE); c.fill()
        if content:
            content(c)
        elif scribble:
            rnd = random.Random(int(t * 8))
            setc(c, RED); c.set_line_width(7)
            c.move_to(-w / 2 + 50, 0)
            for i in range(14):
                c.line_to(-w / 2 + 50 + i * (w - 100) / 13, (rnd.random() - 0.5) * h * 0.55)
            c.stroke()


def tear(c, x, y, t):
    k = (t * 1.2) % 1
    with xf(c, x, y + 60 * k, alpha=1 - k):
        c.move_to(0, -22); c.curve_to(18, 0, 18, 22, 0, 22); c.curve_to(-18, 22, -18, 0, 0, -22)
        fs(c, hexc("#5DADE2"), 4)


def follow_button(c, x, y, s, pressed=0.0):
    with xf(c, x, y, s=s * (1 - 0.08 * pressed)):
        rrect(c, -230, -70 + 14, 460, 140, 70); setc(c, INK); c.fill()
        rrect(c, -230, -70 + 14 * pressed, 460, 140, 70); fs(c, RED if pressed < 0.5 else hexc("#7F8C8D"))
        text(c, "FOLLOW" if pressed < 0.5 else "FOLLOWING", 0, 26 + 14 * pressed, 72, WHITE)


def hand_cursor(c, x, y, s=1.0):
    with xf(c, x, y, s=s, rot=-20):
        rrect(c, -22, -110, 44, 120, 22); fs(c, hexc("#E3A97F"))
        rrect(c, -55, -20, 110, 110, 34); fs(c, hexc("#E3A97F"))


def padlock(c, x, y, s):
    with xf(c, x, y, s=s):
        c.new_path(); c.arc(0, -40, 60, math.pi, 2 * math.pi)
        setc(c, INK); c.set_line_width(36); c.stroke_preserve(); setc(c, hexc("#9AA5AE")); c.set_line_width(22); c.stroke()
        rrect(c, -95, -45, 190, 150, 20); fs(c, GOLD)
        circle(c, 0, 20, 18); setc(c, INK); c.fill()
        rrect(c, -7, 25, 14, 45, 4); c.fill()


