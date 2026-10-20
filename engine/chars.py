"""Character rig v2: bobblehead archetype cast.

person(c, x, y, spec, s=1, ...) draws a character with feet at (x, y); at s=1 they are ~560px tall
with a huge head (~half the height), big expressive eyes, noodle arms and stubby legs.

Expressions: smile happy neutral worried angry shocked sad dreamy smug yell think
             hearts dollars dizzy jawdrop popeyes cry
"""
import math, random
import numpy as np
import cairo
from core import *
from props import sparkles, crown, heart

# ---------------------------------------------------------------- voice-driven lip sync
VOICE_ENV = None


def set_voice_env(env):
    global VOICE_ENV
    VOICE_ENV = env


def voice_level(t):
    if VOICE_ENV is None:
        return 0.5 + 0.5 * math.sin(t * 22)
    i = int(t * FPS)
    return float(VOICE_ENV[i]) if 0 <= i < len(VOICE_ENV) else 0.0


def squash(t, t0, dur=0.5):
    """(sx, sy) for a squash-and-stretch pop-in; (0, 0) before t0, (1, 1) when settled"""
    if t0 is None:
        return 1.0, 1.0
    if t < t0:
        return 0.0, 0.0
    p = prog(t, t0, dur)
    base = back(clamp(p * 1.7), 2.2)
    w = math.sin(p * math.pi * 3.2) * (1 - p) * 0.32
    return base * (1 - w), base * (1 + w)


# ---------------------------------------------------------------- drawing helpers
def noodle(c, p0, p1, p2, width, col):
    for w_, cl in ((width + 2 * LW, INK), (width, col)):
        c.move_to(*p0)
        c.curve_to(p1[0], p1[1], p1[0], p1[1], p2[0], p2[1])
        c.set_line_width(w_)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        setc(c, cl)
        c.stroke()


def ellipse(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(rx, ry); c.new_sub_path(); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()


def darker(col, k=0.8):
    return (col[0] * k, col[1] * k, col[2] * k, col[3])


# ---------------------------------------------------------------- hair
def _cap(c, fringe, top=-556):
    """hair cap over the head top; fringe = points from right to left along the bottom edge"""
    c.move_to(-160, -415)
    c.curve_to(-165, -520, -95, top, 0, top)
    c.curve_to(95, top, 165, -520, 160, -415)
    for p in fringe:
        c.line_to(*p)
    c.close_path()


def hair_back(c, spec, t):
    h = spec["hair"]; col = hexc(spec["hair_c"])
    if h in ("long", "bangs"):
        rrect(c, -174, -548, 348, 335, 140); fs(c, col)
    elif h == "wavy":
        c.new_path()
        rrect(c, -176, -550, 352, 420, 150)
        for i in range(6):
            yy = -420 + i * 55
            circle(c, -176, yy, 34); circle(c, 176, yy, 34)
        setc(c, INK); c.set_line_width(LW * 2); c.stroke_preserve(); setc(c, col); c.fill()
    elif h == "bob":
        rrect(c, -174, -548, 348, 262, 120); fs(c, col)
    elif h == "bighair":
        c.new_path()
        for (cx, cy, r) in ((0, -530, 160), (-150, -470, 100), (150, -470, 100), (-120, -580, 95),
                            (120, -580, 95), (0, -640, 105), (-185, -380, 70), (185, -380, 70)):
            circle(c, cx, cy, r)
        setc(c, INK); c.set_line_width(LW * 2); c.stroke_preserve(); setc(c, col); c.fill()
    elif h == "afro":
        c.new_path()
        for i in range(14):
            a = i * 2 * math.pi / 14
            circle(c, 175 * math.cos(a), -470 + 150 * math.sin(a), 70)
        circle(c, 0, -470, 180)
        setc(c, INK); c.set_line_width(LW * 2); c.stroke_preserve(); setc(c, col); c.fill()
    elif h == "ponytail":
        sw = 10 * math.sin(t * 3)
        c.move_to(120, -500)
        c.curve_to(260 + sw, -520, 260 + sw, -330, 200 + sw, -280)
        c.curve_to(210, -380, 170, -430, 110, -440)
        c.close_path(); fs(c, col)
    elif h == "bun":
        circle(c, 0, -585, 58); fs(c, col)


def hair_front(c, spec, t):
    h = spec["hair"]; col = hexc(spec["hair_c"])
    if h == "spiky":
        for i, sx in enumerate((-110, -55, 0, 55, 110)):
            lean = sx * 0.35
            poly(c, [(sx - 42, -520), (sx + lean, -615 - (20 if i == 2 else 0)), (sx + 42, -520)])
            fs(c, col)
        _cap(c, [(130, -470), (95, -445), (60, -475), (20, -448), (-20, -478), (-60, -450), (-100, -478), (-140, -445)])
        fs(c, col)
    elif h in ("long", "wavy", "bangs"):
        _cap(c, [(150, -400), (90, -470), (20, -490), (-40, -462), (-120, -470), (-150, -400)])
        fs(c, col)
        if h == "bangs":
            c.move_to(-160, -430); c.curve_to(-150, -520, -20, -540, 20, -480)
            c.curve_to(10, -420, -40, -370, -110, -340); c.curve_to(-140, -360, -160, -390, -160, -430)
            fs(c, col)
    elif h == "bob":
        _cap(c, [(160, -330), (140, -330), (140, -455), (-140, -455), (-140, -330), (-160, -330)])
        fs(c, col)
    elif h == "bighair":
        pts = [(150, -440)]
        for i in range(7):
            x0 = 150 - (i + 0.5) * 300 / 7
            pts += [(x0, -505 + 18 * (i % 2)), (x0 - 300 / 14, -470)]
        _cap(c, pts + [(-150, -440)], top=-570)
        fs(c, col)
    elif h == "afro":
        pts = []
        for i in range(8):
            x0 = 150 - i * 300 / 7
            pts += [(x0, -480), (x0 - 20, -505)]
        _cap(c, pts, top=-570)
        fs(c, col)
    elif h in ("short", "ponytail", "bun", "quiff"):
        _cap(c, [(150, -440), (100, -480), (20, -470), (-60, -490), (-140, -455)])
        fs(c, col)
        if h == "quiff":
            ellipse(c, 15, -560, 140, 62); fs(c, col)
            c.move_to(-60, -560); c.curve_to(-20, -600, 60, -605, 120, -575)
            setc(c, hexc("#FFFFFF", 0.35)); c.set_line_width(8); c.stroke()
        if h == "ponytail":
            circle(c, 135, -495, 18); fs(c, hexc("#E74C3C"), 5)
    elif h == "curlers":
        _cap(c, [(150, -440), (60, -470), (-60, -470), (-150, -440)])
        fs(c, col)
        for i, cx in enumerate((-100, -35, 35, 100)):
            rrect(c, cx - 26, -585 + abs(cx) * 0.25, 52, 48, 14)
            fs(c, hexc(("#F7A8B8", "#86D3F5", "#F9D96A", "#A8E6A1")[i]), 5)
    elif h == "comb":
        for sx in (-1, 1):
            circle(c, sx * 150, -440, 45); fs(c, col)
        setc(c, INK); c.set_line_width(6)
        for k in (-40, 0, 40):
            c.move_to(k - 30, -535); c.curve_to(k - 10, -575, k + 20, -575, k + 40, -545)
        c.stroke()


# ---------------------------------------------------------------- face
def _gaze(t, seed, look):
    if look is not None:
        return look
    k = math.floor((t + seed * 0.37) * 0.75)
    return 10 * math.sin(k * 2.3 + seed), 4 * math.sin(k * 1.7)


def _eyes(c, expr, t, seed, look, blink):
    ex, ey = 60, -420
    gx, gy = _gaze(t, seed, look)
    if expr == "think":
        gx, gy = 8, -10
    for side in (-1, 1):
        x = side * ex
        if expr in ("happy", "dollars_closed"):
            c.new_path(); c.arc(x, ey + 10, 26, math.pi * 1.1, math.pi * 1.9)
            setc(c, INK); c.set_line_width(10); c.stroke()
            continue
        if expr == "hearts":
            heart(c, x, ey, 0.55 + 0.08 * math.sin(t * 12))
            continue
        if expr == "dollars":
            ellipse(c, x, ey, 34, 38); fs(c, hexc("#B8F5B0"), 5)
            text(c, "$", x, ey + 22, 64, hexc("#1E8B3A"))
            continue
        if expr == "dizzy":
            ellipse(c, x, ey, 32, 36); fs(c, WHITE, 5)
            setc(c, INK); c.set_line_width(5)
            for i in range(28):
                a = i * 0.45 + t * 9 * side
                r = 2 + i * 0.95
                (c.move_to if i == 0 else c.line_to)(x + r * math.cos(a), ey + r * math.sin(a))
            c.stroke()
            continue
        if blink and expr not in ("shocked", "popeyes", "jawdrop"):
            c.move_to(x - 26, ey + 4); c.curve_to(x - 10, ey + 14, x + 10, ey + 14, x + 26, ey + 4)
            setc(c, INK); c.set_line_width(8); c.stroke()
            continue
        rx, ry, pr = 32, 38, 15
        if expr in ("shocked", "jawdrop"):
            rx, ry, pr = 44, 52, 8
        if expr == "popeyes":
            k = 1 + 0.12 * math.sin(t * 30)
            rx, ry, pr = 62 * k, 72 * k, 9
            limb(c, [(x, ey + 10), (x + side * 10, ey - 40)], 14, WHITE)
            ey2 = ey - 50
        else:
            ey2 = ey
        ellipse(c, x, ey2, rx, ry); fs(c, WHITE, 6)
        px = x + (gx * 0.4 if expr in ("shocked", "jawdrop", "popeyes") else gx)
        py = ey2 + (gy if expr not in ("sad", "cry") else 8)
        if expr in ("sad", "cry", "worried"):
            pr = 18
        circle(c, px, py, pr); setc(c, INK); c.fill()
        circle(c, px + pr * 0.35, py - pr * 0.4, max(3, pr * 0.32)); setc(c, WHITE); c.fill()
        # lids
        skin = _SKIN
        if expr == "determined":
            o, i_ = x + side * (rx + 4), x - side * (rx + 4)
            c.save(); ellipse(c, x, ey2, rx, ry); c.clip()
            poly(c, [(o, ey2 - ry - 4), (i_, ey2 - ry - 4), (i_, ey2 - ry * 0.05), (o, ey2 - ry * 0.45)])
            setc(c, skin); c.fill()
            poly(c, [(o, ey2 + ry + 4), (i_, ey2 + ry + 4), (i_, ey2 + ry * 0.6), (o, ey2 + ry * 0.7)])
            c.fill(); c.restore()
            c.move_to(o, ey2 - ry * 0.45); c.line_to(i_, ey2 - ry * 0.05); setc(c, INK); c.set_line_width(9); c.stroke()
        elif expr in ("dreamy", "smug"):
            lid = {"smug": 6, "dreamy": 0}[expr]
            c.save(); ellipse(c, x, ey2, rx, ry); c.clip()
            c.rectangle(x - rx - 2, ey2 - ry - 2, 2 * rx + 4, ry + lid); setc(c, skin); c.fill()
            c.restore()
            c.move_to(x - rx, ey2 + lid); c.line_to(x + rx, ey2 + lid)
            setc(c, INK); c.set_line_width(8); c.stroke()
        elif expr in ("angry", "yell"):
            c.save(); ellipse(c, x, ey2, rx, ry); c.clip()
            o, i_ = x + side * (rx + 4), x - side * (rx + 4)
            poly(c, [(o, ey2 - ry - 4), (i_, ey2 - ry - 4), (i_, ey2 + 2), (o, ey2 - ry * 0.55)])
            setc(c, skin); c.fill(); c.restore()
            c.move_to(o, ey2 - ry * 0.55); c.line_to(i_, ey2 + 2); setc(c, INK); c.set_line_width(7); c.stroke()
        elif expr in ("sad", "cry"):
            c.save(); ellipse(c, x, ey2, rx, ry); c.clip()
            o, i_ = x + side * (rx + 4), x - side * (rx + 4)
            poly(c, [(o, ey2 - ry - 4), (i_, ey2 - ry - 4), (i_, ey2 - ry * 0.6), (o, ey2 - 2)])
            setc(c, skin); c.fill(); c.restore()
            c.move_to(i_, ey2 - ry * 0.6); c.line_to(o, ey2 - 2); setc(c, INK); c.set_line_width(7); c.stroke()
        ellipse(c, x, ey2, rx, ry); setc(c, INK); c.set_line_width(6); c.stroke()


def _brows(c, expr, t):
    by = -488
    setc(c, INK); c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for side in (-1, 1):
        x = side * 60
        if expr in ("angry", "yell"):
            c.move_to(x + side * 38, by - 14); c.line_to(x - side * 30, by + 18)
        elif expr in ("worried", "sad", "cry"):
            c.move_to(x + side * 36, by + 12); c.line_to(x - side * 30, by - 12)
        elif expr in ("shocked", "jawdrop", "popeyes"):
            c.move_to(x - 30, by - 34); c.curve_to(x - 10, by - 50, x + 10, by - 50, x + 30, by - 34)
        elif expr == "think":
            if side < 0:
                c.move_to(x - 32, by + 4); c.line_to(x + 30, by + 4)
            else:
                c.move_to(x - 30, by - 22); c.curve_to(x - 10, by - 38, x + 10, by - 38, x + 32, by - 20)
        elif expr == "smug":
            c.move_to(x - 30, by - (14 if side > 0 else 0)); c.line_to(x + 30, by - (4 if side > 0 else 6))
        elif expr == "determined":
            c.move_to(x + side * 40, by - 4); c.line_to(x - side * 34, by + 22)
        else:
            c.move_to(x - 30, by - 6); c.curve_to(x - 10, by - 18, x + 10, by - 18, x + 30, by - 6)
    c.stroke()


def _nose(c, spec):
    n = spec.get("nose", "small")
    skin = hexc(spec["skin"])
    if n == "big":
        ellipse(c, 6, -368, 34, 27); fs(c, darker(skin, 0.93), 6)
        circle(c, 18, -376, 6); setc(c, WHITE[:3] + (0.6,)); c.fill()
    elif n == "button":
        circle(c, 0, -370, 12); setc(c, hexc("#E8907A")); c.fill()
    else:
        c.new_path(); c.arc(0, -378, 14, math.pi * 0.15, math.pi * 0.85)
        setc(c, INK); c.set_line_width(6); c.stroke()


_SKIN = (1, 0.8, 0.6, 1)
MOUTH_RED = hexc("#7A1F1F")
TONGUE = hexc("#E86A6A")


def _mouth(c, expr, t, talk):
    my = -318
    if talk:
        lv = voice_level(t)
        h = 10 + 50 * clamp(lv)
        ellipse(c, 0, my + h * 0.3, 34 + 6 * lv, h * 0.7 + 4); fs(c, MOUTH_RED, 7)
        if h > 25:
            ellipse(c, 0, my + h * 0.55, 18, h * 0.22); setc(c, TONGUE); c.fill()
        return
    if expr == "jawdrop":
        drop = 40 + 18 * math.sin(t * 4)
        rrect(c, -48, my - 18, 96, 200 + drop, 46); fs(c, MOUTH_RED, 7)
        rrect(c, -40, my - 14, 80, 24, 8); fs(c, WHITE, 4)
        ellipse(c, 0, my + 150 + drop, 34, 46); fs(c, TONGUE, 6)
    elif expr in ("happy", "hearts", "dollars", "dreamy"):
        c.move_to(-62, my - 20); c.curve_to(-50, my + 52, 50, my + 52, 62, my - 20); c.close_path()
        fs(c, MOUTH_RED, 7)
        c.save(); c.move_to(-62, my - 20); c.curve_to(-50, my + 52, 50, my + 52, 62, my - 20); c.close_path(); c.clip()
        c.rectangle(-70, my - 22, 140, 16); setc(c, WHITE); c.fill()
        ellipse(c, 0, my + 32, 30, 16); setc(c, TONGUE); c.fill()
        c.restore()
        c.move_to(-62, my - 20); c.curve_to(-50, my + 52, 50, my + 52, 62, my - 20); c.close_path()
        setc(c, INK); c.set_line_width(7); c.stroke()
    elif expr == "smile":
        c.new_path(); c.arc(0, my - 34, 46, math.pi * 0.2, math.pi * 0.8)
        setc(c, INK); c.set_line_width(9); c.stroke()
    elif expr in ("smug", "determined"):
        c.move_to(-36, my); c.curve_to(-10, my + 12, 20, my + 6, 46, my - 18)
        setc(c, INK); c.set_line_width(9); c.stroke()
    elif expr == "yell":
        poly(c, [(-58, my - 26), (58, my - 26), (40, my + 44), (-40, my + 44)]); fs(c, MOUTH_RED, 7)
        rrect(c, -50, my - 24, 100, 16, 4); fs(c, WHITE, 4)
        ellipse(c, 0, my + 30, 24, 10); setc(c, TONGUE); c.fill()
    elif expr in ("shocked", "popeyes"):
        ellipse(c, 0, my + 8, 26, 36); fs(c, MOUTH_RED, 7)
    elif expr in ("sad", "cry", "angry"):
        c.new_path(); c.arc(0, my + 30, 38, math.pi * 1.2, math.pi * 1.8)
        setc(c, INK); c.set_line_width(9); c.stroke()
    elif expr in ("worried", "dizzy"):
        c.move_to(-40, my)
        for i in range(1, 9):
            c.line_to(-40 + i * 10, my + (8 if i % 2 else -2))
        setc(c, INK); c.set_line_width(7); c.stroke()
    elif expr == "think":
        c.move_to(-20, my + 4); c.line_to(30, my - 6); setc(c, INK); c.set_line_width(8); c.stroke()
    else:
        c.move_to(-30, my); c.line_to(30, my); setc(c, INK); c.set_line_width(8); c.stroke()


def _auto_fx(c, spec, expr, t, seed):
    if expr in ("worried", "shocked", "jawdrop", "popeyes") or spec.get("sweaty"):
        for i, (sx, ph) in enumerate(((150, 0.0), (-160, 0.5))):
            k = ((t * 1.3) + ph + seed * 0.1) % 1
            with xf(c, sx, -500 + 120 * k, s=0.9, alpha=1 - k):
                c.move_to(0, -26); c.curve_to(20, 0, 20, 24, 0, 24); c.curve_to(-20, 24, -20, 0, 0, -26)
                fs(c, hexc("#8FD3F5"), 5)
    if expr in ("angry", "yell") and spec.get("steam", True):
        for side in (-1, 1):
            for i in range(3):
                k = ((t * 1.6) + i / 3) % 1
                circle(c, side * (175 + 40 * k), -470 - 120 * k, 18 + 26 * k)
                setc(c, hexc("#FFFFFF", 0.9 * (1 - k))); c.fill_preserve()
                setc(c, INK[:3] + (0.8 * (1 - k),)); c.set_line_width(4); c.stroke()
    if expr == "cry":
        for side in (-1, 1):
            for i in range(4):
                k = ((t * 2.2) + i / 4) % 1
                circle(c, side * (70 + 30 * k), -380 + 170 * k, 12)
                setc(c, hexc("#5DADE2", 0.9)); c.fill()
    if expr == "dizzy":
        for i in range(3):
            a = t * 3 + i * 2.1
            with xf(c, 140 * math.cos(a), -590 + 30 * math.sin(a), s=0.7):
                poly(c, [(30 * (1 if j % 2 == 0 else 0.45) * math.cos(-math.pi / 2 + j * math.pi / 5),
                          30 * (1 if j % 2 == 0 else 0.45) * math.sin(-math.pi / 2 + j * math.pi / 5)) for j in range(10)])
                fs(c, GOLD, 4)


# ---------------------------------------------------------------- body
def _baby_body(c, spec, top, skin, walk_ph, walking):
    """chubby toddler: short thick legs, bare feet, round torso, diaper"""
    for side in (-1, 1):
        sw = math.sin(walk_ph) * 26 * side if walking else 0
        lift = max(0, math.sin(walk_ph) * side) * 20 if walking else 0
        hip = (side * 36, -118)
        foot = (side * 44 + sw, -lift - 6)
        noodle(c, hip, (side * 50 + sw * 0.4, -60), foot, 44, skin)
        ellipse(c, foot[0] + side * 8, foot[1] - 2, 34, 20); fs(c, skin, 6)
    cw = 96 if spec.get("muscles") else 84
    rrect(c, -cw, -296, 2 * cw, 196, 74); fs(c, top)
    if spec["outfit"] == "tank":
        trim = hexc(spec.get("trim_c", "#22305A"))
        c.new_path(); c.arc(0, -300, 46, 0.1 * math.pi, 0.9 * math.pi)
        setc(c, trim); c.set_line_width(12); c.stroke()
        for side in (-1, 1):
            c.new_path(); c.arc(side * cw, -250, 40, (0.5 if side < 0 else -0.5) * math.pi + (0 if side > 0 else 0),
                                (1.5 if side < 0 else 0.5) * math.pi)
            setc(c, trim); c.set_line_width(12); c.stroke()
    if spec["outfit"] == "suit":
        poly(c, [(-34, -232), (34, -232), (0, -150)]); fs(c, WHITE, 5)
        poly(c, [(-11, -228), (11, -228), (15, -178), (0, -156), (-15, -178)]); fs(c, RED, 4)
        for side in (-1, 1):
            circle(c, side * 52, -190, 7); setc(c, GOLD); c.fill()
    if spec.get("logo") == "bolt":
        poly(c, [(8, -262), (-22, -212), (0, -212), (-10, -176), (24, -228), (2, -228)]); fs(c, GOLD, 5)
    # diaper
    c.move_to(-88, -150); c.line_to(88, -150); c.curve_to(92, -100, 60, -78, 0, -76)
    c.curve_to(-60, -78, -92, -100, -88, -150); c.close_path(); fs(c, WHITE)
    for side in (-1, 1):
        rrect(c, side * 62 - 14, -150, 28, 22, 6); fs(c, hexc("#86D3F5"), 4)
    if spec.get("chain"):
        c.new_path(); c.arc(0, -330, 95, math.pi * 0.27, math.pi * 0.73)
        setc(c, INK); c.set_line_width(14); c.stroke_preserve(); setc(c, GOLD); c.set_line_width(7); c.stroke()
        # pacifier pendant
        circle(c, 0, -222, 16); setc(c, INK); c.set_line_width(12); c.stroke_preserve()
        setc(c, GOLD); c.set_line_width(6); c.stroke()
        ellipse(c, 0, -196, 34, 18); fs(c, hexc("#86D3F5"), 5)
        circle(c, 0, -180, 10); fs(c, hexc("#F5D76E"), 4)


def _body(c, spec, top, bottom, skin, walk_ph, walking):
    outfit = spec["outfit"]
    if spec.get("baby"):
        return _baby_body(c, spec, top, skin, walk_ph, walking)
    # legs
    for side in (-1, 1):
        sw = math.sin(walk_ph) * 30 * side if walking else 0
        lift = max(0, math.sin(walk_ph) * side) * 22 if walking else 0
        hip = (side * 30, -150)
        foot = (side * 36 + sw, -lift)
        noodle(c, hip, (side * 40 + sw * 0.4, -80), foot, 28, skin if outfit == "dress" else bottom)
        ellipse(c, foot[0] + side * 10, foot[1] - 4, 34, 16)
        fs(c, hexc("#3A2A22") if outfit != "suit" else INK, 5)
    # torso
    if outfit == "dress":
        c.move_to(-58, -285); c.line_to(58, -285)
        c.curve_to(72, -210, 115, -130, 128, -96); c.line_to(-128, -96)
        c.curve_to(-115, -130, -72, -210, -58, -285); c.close_path()
        fs(c, top)
        if spec.get("trim"):
            c.move_to(-122, -110); c.line_to(122, -110); setc(c, GOLD); c.set_line_width(10); c.stroke()
    else:
        rrect(c, -70, -290, 140, 160, 46); fs(c, top)
        if outfit == "suit":
            poly(c, [(-26, -290), (26, -290), (0, -215)]); fs(c, WHITE, 5)
            poly(c, [(-9, -282), (9, -282), (13, -232), (0, -214), (-13, -232)]); fs(c, RED, 4)
        elif spec.get("logo"):
            circle(c, 0, -215, 26); fs(c, hexc("#FFFFFF", 0.85), 5)
            text(c, spec["logo"], 0, -203, 34, top)
    if spec.get("apron"):
        rrect(c, -48, -235, 96, 120, 18); fs(c, WHITE, 6)
        heart(c, 0, -185, 0.3, "#F08A8A")



def _head_path(c, spec):
    if spec.get("head") == "jaw":
        c.move_to(-150, -420)
        c.curve_to(-150, -565, 150, -565, 150, -420)
        c.line_to(150, -335)
        c.curve_to(150, -282, 112, -256, 60, -254)
        c.line_to(-60, -254)
        c.curve_to(-112, -256, -150, -282, -150, -335)
        c.close_path()
    else:
        rrect(c, -152, -540, 304, 272, 128)


# ---------------------------------------------------------------- adult hero rig (muscular, cel-shaded)
ADULT_SCALE = 0.9      # overall size so he stands a little taller than the bobblehead cast
ADULT_HEAD_K = 0.84    # head scale relative to the bobblehead head
ADULT_HEAD_Y = -582    # where the (scaled) head centre sits on the adult body
RIM = hexc("#FFD7A0")


def _torso_path(c):
    c.move_to(-62, -448)
    c.curve_to(-100, -446, -132, -430, -136, -398)
    c.curve_to(-140, -350, -118, -300, -84, -226)
    c.line_to(84, -226)
    c.curve_to(118, -300, 140, -350, 136, -398)
    c.curve_to(132, -430, 100, -446, 62, -448)
    c.close_path()


def _adult_arm(c, side, a, b, spec, skin, t, pointer):
    sleeve = hexc(spec.get("sleeve_c", spec["top"]))
    sh = (side * 126, -402)
    l1, l2 = 128, 118
    a1 = math.radians(a)
    el = (sh[0] + side * l1 * math.sin(a1), sh[1] + l1 * math.cos(a1))
    a2 = math.radians(a + b)
    dx, dy = side * math.sin(a2), math.cos(a2)
    hd = (el[0] + l2 * dx, el[1] + l2 * dy)
    noodle(c, el, el, hd, 54, skin)                               # forearm
    cuff = (el[0] + l2 * 0.12 * dx, el[1] + l2 * 0.12 * dy)
    mx, my = sh[0] + (el[0] - sh[0]) * 0.5, sh[1] + (el[1] - sh[1]) * 0.5
    nx, ny = -(el[1] - sh[1]) / l1, (el[0] - sh[0]) / l1
    if ny > 0:
        nx, ny = -nx, -ny
    bx, by = mx + nx * 14, my + ny * 14
    for k, col in ((2 * LW, INK), (0, sleeve)):
        c.move_to(*sh); c.line_to(*el); c.line_to(*cuff)
        c.set_line_width(72 + k); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(c, col); c.stroke()
        ellipse(c, bx, by, 46 + k / 2, 42 + k / 2); setc(c, col); c.fill()
    setc(c, hexc("#FFFFFF", 0.2)); c.set_line_width(9)
    c.move_to(bx + nx * 18 - (el[0] - sh[0]) * 0.25, by + ny * 18 - (el[1] - sh[1]) * 0.25)
    c.line_to(bx + nx * 18 + (el[0] - sh[0]) * 0.2, by + ny * 18 + (el[1] - sh[1]) * 0.2); c.stroke()
    # hand: fist, or a pointing finger along the forearm
    if pointer:
        limb(c, [hd, (hd[0] + 50 * dx, hd[1] + 50 * dy)], 18, skin)
    circle(c, hd[0], hd[1], 31); fs(c, skin, 6)
    return hd


def _adult_body(c, spec, arms, skin, t, seed, bob, walk_ph, walking, point):
    top = hexc(spec["top"]); jeans = hexc(spec.get("bottom", "#2E3F66"))
    # legs + boots
    for side in (-1, 1):
        sw = math.sin(walk_ph) * 34 * side if walking else 0
        lift = max(0, math.sin(walk_ph) * side) * 26 if walking else 0
        hip = (side * 44, -222)
        foot = (side * 50 + sw, -lift - 14)
        noodle(c, hip, (side * 52 + sw * 0.4, -110), foot, 56, jeans)
        rrect(c, foot[0] - 30 + side * 8, foot[1] - 18, 68, 34, 14); fs(c, hexc("#4A3326"), 6)
    rrect(c, -86, -240, 172, 28, 8); fs(c, hexc("#3A2A20"), 5)
    rrect(c, -16, -238, 32, 24, 4); fs(c, hexc("#C9C9C9"), 4)
    # neck (behind the collar)
    rrect(c, -50, -492, 100, 70, 22); fs(c, skin, 6)
    c.rectangle(-46, -490, 92, 22); setc(c, INK[:3] + (0.18,)); c.fill()
    # torso: heather body, raglan sleeves, henley placket, pecs, shading + rim light
    _torso_path(c); fs(c, top)
    c.save(); _torso_path(c); c.clip()
    sleeve = hexc(spec.get("sleeve_c", spec["top"]))
    for side in (-1, 1):
        poly(c, [(side * 44, -452), (side * 140, -452), (side * 140, -330), (side * 118, -330)])
        setc(c, sleeve); c.fill()
    c.move_to(30, -450); c.curve_to(70, -380, 90, -300, 60, -226); c.line_to(150, -226); c.line_to(150, -450)
    c.close_path(); setc(c, INK[:3] + (0.16,)); c.fill()
    setc(c, RIM[:3] + (0.55,)); c.set_line_width(10)
    c.move_to(-128, -400); c.curve_to(-132, -350, -114, -300, -82, -232); c.stroke()
    c.restore()
    _torso_path(c); setc(c, INK); c.set_line_width(LW); c.stroke()
    for side in (-1, 1):
        c.move_to(side * 98, -360); c.curve_to(side * 70, -320, side * 25, -322, side * 6, -345)
    setc(c, INK[:3] + (0.35,)); c.set_line_width(5); c.stroke()
    ellipse(c, 0, -450, 58, 16); fs(c, skin, 6)
    c.new_path(); c.arc(0, -452, 60, 0.05 * math.pi, 0.95 * math.pi)
    setc(c, sleeve); c.set_line_width(10); c.stroke()
    rrect(c, -11, -440, 22, 74, 5); fs(c, darker(top, 0.85), 4)
    for by in (-420, -392):
        circle(c, 0, by, 5); setc(c, INK); c.fill()
    # arms
    hands = []
    if arms == "crossed":
        for side in (1, -1):
            sh, el = (side * 126, -402), (side * 150, -296)
            hd = (-side * 76, -338 + side * 10)
            noodle(c, el, el, hd, 54, skin)
            for k, col in ((2 * LW, INK), (0, sleeve)):
                c.move_to(*sh); c.line_to(*el); c.line_to(el[0] - side * 18, el[1] - 6)
                c.set_line_width(72 + k); c.set_line_cap(cairo.LINE_CAP_ROUND); setc(c, col); c.stroke()
                ellipse(c, side * 146, -352, 46 + k / 2, 48 + k / 2); setc(c, col); c.fill()
            circle(c, hd[0], hd[1], 31); fs(c, skin, 6)
            hands.append(hd)
        hands.reverse()
        return hands
    la, lb, ra, rb = arms
    wob = 2.5 * math.sin(t * 3 + seed) if bob else 0
    for side, a, b in ((-1, la + wob, lb), (1, ra - wob, rb)):
        hands.append(_adult_arm(c, side, a, b, spec, skin, t, point == ("l" if side < 0 else "r")))
    return hands


def person(c, x, y, spec, s=1.0, expr="neutral", arms=(12, 0, 12, 0), t=0.0, talk=False,
           flip=False, bob=True, blink_seed=0, hold=None, alpha=1.0, glow=False, extra=None,
           born=None, walk=False, look=None, hold_l=None, point=None):
    """arms = (left_angle, left_bend, right_angle, right_bend), degrees; 0 = hanging down,
    positive angle = away from the body, negative bend = forearm folds inward.
    born = time the character pops in (squash & stretch). walk = leg cycle + body bounce."""
    skin = hexc(spec["skin"]); top = hexc(spec["top"]); bottom = hexc(spec.get("bottom", "#2E3A5C"))
    sx_, sy_ = squash(t, born)
    if sx_ <= 0:
        return
    seed = blink_seed
    breath = 1 + (0.015 * math.sin(t * 2.6 + seed) if bob else 0)
    walk_ph = t * 10
    hop = abs(math.sin(walk_ph)) * 14 if walk else 0
    fl = (-45 - 18 * math.sin(t * 2.2 + seed)) if spec.get("float") else 0
    period = 3.1 + (seed % 5) * 0.37
    blink = ((t + seed + 1.5) % period) < 0.12
    sway = 2.5 * math.sin(t * 1.7 + seed) if bob else 0
    # ground shadow
    with xf(c, x, y, s=s):
        ellipse(c, 0, 0, 100 * sx_, 16 * sx_)
        setc(c, INK[:3] + (0.12 * alpha,)); c.fill()
    if glow:
        g = cairo.RadialGradient(x, y - 320 * s + fl * s, 20 * s, x, y - 320 * s + fl * s, 440 * s)
        g.add_color_stop_rgba(0, 1, 0.88, 0.35, 0.8 * alpha)
        g.add_color_stop_rgba(1, 1, 0.88, 0.35, 0)
        c.set_source(g); c.arc(x, y - 320 * s + fl * s, 440 * s, 0, 2 * math.pi); c.fill()
    with xf(c, x, y + (fl - hop) * s, sx=s * sx_ * (-1 if flip else 1), sy=s * sy_ * breath, alpha=alpha, rot=0):
        c.rotate(math.radians(sway * 0.4))
        global _SKIN
        _SKIN = skin
        if spec.get("wings"):
            for side in (-1, 1):
                fl_ap = 10 * math.sin(t * 6)
                c.move_to(side * 40, -250)
                c.curve_to(side * 200, -420 - fl_ap, side * 260, -260, side * 230, -170)
                c.curve_to(side * 180, -200, side * 150, -150, side * 60, -190); c.close_path()
                fs(c, WHITE)
        hair_back(c, spec, t)
        if spec.get("veil"):
            c.move_to(-90, -520); c.curve_to(-210, -420, -190, -230, -170, -130)
            c.line_to(170, -130); c.curve_to(190, -230, 210, -420, 90, -520); c.close_path()
            setc(c, hexc("#FFFFFF", 0.8)); c.fill_preserve(); setc(c, INK); c.set_line_width(5); c.stroke()
        adult = spec.get("rig") == "adult"
        if adult:
            c.scale(ADULT_SCALE, ADULT_SCALE)
            adult_hands = _adult_body(c, spec, arms, skin, t, seed, bob, walk_ph, walk, point)
        else:
            _body(c, spec, top, bottom, skin, walk_ph, walk)

        def _draw_arms():
            # arms (noodles with idle wobble)
            crossed = arms == "crossed"
            la, lb, ra, rb = (14, 0, 14, 0) if crossed else arms
            wob = 3 * math.sin(t * 3 + seed) if bob else 0
            hands = []
            if crossed:
                aw = 36 if spec.get("muscles") else 26
                for side in (1, -1):
                    sh, el, hd = (side * 60, -255), (side * 100, -172), (-side * 40, -208 + side * 8)
                    noodle(c, sh, el, hd, aw, skin)
                    if spec.get("muscles"):
                        circle(c, side * 92, -222, 26); fs(c, skin, 6)
                    if spec["outfit"] != "tank":
                        limb(c, [sh, (side * 74, -228)], aw + 12,
                             hexc(spec["sleeve_c"]) if spec.get("sleeve_c") else top)
                    circle(c, hd[0], hd[1], 21); fs(c, skin, 6)
                    hands.append(hd)
                hands.reverse()
            for side, a, b in (() if crossed else ((-1, la + wob, lb), (1, ra - wob, rb))):
                big = spec.get("muscles")
                sh = (side * (72 if big else 56), -255)
                l1, l2 = (100, 86) if big else (82, 78)
                a1 = math.radians(a)
                el = (sh[0] + side * l1 * math.sin(a1), sh[1] + l1 * math.cos(a1))
                a2 = math.radians(a + b)
                hd = (el[0] + side * l2 * math.sin(a2), el[1] + l2 * math.cos(a2))
                sleeve = top if spec["outfit"] != "dress" or spec.get("sleeves") else skin
                noodle(c, sh, el, hd, 40 if spec.get("muscles") else 26, skin)
                if spec.get("muscles"):
                    # deltoid cap + a bicep that pops when the forearm is folded up (flex)
                    if b > 40:
                        mx, my = sh[0] + (el[0] - sh[0]) * 0.55, sh[1] + (el[1] - sh[1]) * 0.55
                        nx, ny = -(el[1] - sh[1]) / l1, (el[0] - sh[0]) / l1
                        flip_ = -1 if ny > 0 else 1
                        ellipse(c, mx + nx * 14 * flip_, my + ny * 14 * flip_, 30, 26); fs(c, skin, 6)
                if spec["outfit"] not in ("dress", "tank") or spec.get("sleeves"):
                    sl = spec.get("sleeve_len", 0.9 if spec["outfit"] == "suit" else 0.5)
                    mid = (sh[0] + (el[0] - sh[0]) * sl, sh[1] + (el[1] - sh[1]) * sl)
                    limb(c, [sh, mid], 46 if big else 36, hexc(spec["sleeve_c"]) if spec.get("sleeve_c") else sleeve)
                circle(c, hd[0], hd[1], 20); fs(c, skin, 6)
                hands.append(hd)
            return hands

        raised = not adult and arms != "crossed" and max(arms[0], arms[2]) > 80
        hands = adult_hands if adult else ([] if raised else _draw_arms())
        if adult:
            c.save(); c.translate(0, ADULT_HEAD_Y); c.scale(ADULT_HEAD_K, ADULT_HEAD_K); c.translate(0, 400)
        # head
        for side in (-1, 1):
            circle(c, side * 150, -405, 26); fs(c, skin, 6)
        if spec.get("head") == "square":
            rrect(c, -142, -540, 284, 280, 60); fs(c, skin)
            rrect(c, -150, -380, 300, 125, 50); fs(c, skin)
            rrect(c, -142, -390, 284, 40, 10); setc(c, skin); c.fill()
            # cleft chin
            c.new_path(); c.arc(0, -262, 14, math.pi * 1.15, math.pi * 1.85); setc(c, INK); c.set_line_width(5); c.stroke()
        else:
            _head_path(c, spec); fs(c, skin)
            if spec.get("head") == "jaw":
                c.new_path(); c.arc(0, -270, 14, math.pi * 1.15, math.pi * 1.85)
                setc(c, INK[:3] + (0.6,)); c.set_line_width(5); c.stroke()
                c.save(); _head_path(c, spec); c.clip()
                c.move_to(70, -560); c.curve_to(140, -480, 150, -330, 100, -250); c.line_to(170, -250); c.line_to(170, -560)
                c.close_path(); setc(c, INK[:3] + (0.12,)); c.fill()
                c.restore()
        hair_front(c, spec, t)
        if spec.get("hair") == "buzz":
            hc = hexc(spec["hair_c"])
            c.save(); _head_path(c, spec); c.clip()
            c.move_to(-160, -390)
            for (bx, by) in ((-160, -560), (160, -560), (160, -390), (140, -440), (110, -470), (55, -478),
                             (0, -464), (-55, -478), (-110, -470), (-140, -440)):
                c.line_to(bx, by)
            c.close_path(); setc(c, hc[:3] + (0.88,)); c.fill()
            rnd = random.Random(8)
            setc(c, hexc("#FFFFFF", 0.12))
            for _ in range(120):
                circle(c, rnd.uniform(-150, 150), rnd.uniform(-540, -480), 2.2)
            c.fill()
            c.restore()
        if spec.get("stubble"):
            c.save(); _head_path(c, spec); c.clip()
            c.move_to(-152, -395); c.curve_to(-120, -360, -80, -350, -60, -350)
            c.curve_to(-30, -362, 30, -362, 60, -350); c.curve_to(80, -350, 120, -360, 152, -395)
            c.line_to(152, -250); c.line_to(-152, -250); c.close_path()
            setc(c, hexc(spec["hair_c"], 0.22)); c.fill()
            rnd = random.Random(4)
            setc(c, hexc(spec["hair_c"], 0.45))
            for _ in range(140):
                bx = rnd.uniform(-140, 140); by = rnd.uniform(-345, -275)
                circle(c, bx, by, 2.2)
            c.fill()
            c.restore()
        if spec.get("hair") == "shaved":
            c.save(); _head_path(c, spec); c.clip()
            rnd = random.Random(5)
            setc(c, hexc(spec["hair_c"], 0.3))
            for _ in range(160):
                bx = rnd.uniform(-150, 150)
                by = rnd.uniform(-545, -470 + 0.25 * abs(bx))
                circle(c, bx, by, 2.6)
            c.fill()
            c.restore()
            ellipse(c, -55, -505, 42, 16); setc(c, hexc("#FFFFFF", 0.55)); c.fill()
        if spec.get("headband"):
            rrect(c, -156, -500, 312, 40, 14); fs(c, hexc(spec["headband"]))
            limb(c, [(150, -480), (205, -455 + 8 * math.sin(t * 5))], 18, hexc(spec["headband"]))
        if spec.get("beard"):
            bc = hexc(spec.get("beard_c", "#2B1A12"))
            c.move_to(-152, -425)
            c.curve_to(-160, -300, -110, -228, 0, -222)
            c.curve_to(110, -228, 160, -300, 152, -425)
            c.curve_to(125, -385, 105, -350, 72, -352)
            c.curve_to(45, -292, -45, -292, -72, -352)
            c.curve_to(-105, -350, -125, -385, -152, -425)
            c.close_path(); fs(c, bc)
            setc(c, hexc("#FFFFFF", 0.18)); c.set_line_width(5)
            for (bx, by) in ((-110, -320), (-60, -270), (0, -258), (60, -270), (110, -320), (-130, -375), (130, -375)):
                c.move_to(bx, by); c.line_to(bx + 6, by + 22)
            c.stroke()
        if spec.get("blush") or expr in ("dreamy", "hearts", "happy", "smile"):
            for side in (-1, 1):
                ellipse(c, side * 102, -362, 28, 15); setc(c, hexc("#F08A8A", 0.6)); c.fill()
        _eyes(c, expr, t, seed, look, blink)
        _brows(c, expr, t)
        _nose(c, spec)
        _mouth(c, expr, t, talk)
        if spec.get("beard"):
            c.move_to(-78, -336); c.curve_to(-40, -378, 40, -378, 78, -336)
            c.curve_to(30, -354, -30, -354, -78, -336); fs(c, hexc(spec.get("beard_c", "#2B1A12")), 5)
        if spec.get("moustache"):
            c.move_to(-60, -338); c.curve_to(-30, -372, 30, -372, 60, -338); c.curve_to(20, -350, -20, -350, -60, -338)
            fs(c, hexc("#D9D9D9"), 5)
        if spec.get("glasses"):
            for side in (-1, 1):
                ellipse(c, side * 60, -420, 46, 46); setc(c, INK); c.set_line_width(7); c.stroke()
            c.move_to(-14, -425); c.line_to(14, -425); c.stroke()
        if spec.get("intense") and expr in ("determined", "angry", "yell", "neutral", "think"):
            setc(c, INK[:3] + (0.55,)); c.set_line_width(5)
            c.move_to(-10, -478); c.line_to(-6, -452); c.move_to(10, -478); c.line_to(6, -452); c.stroke()
        if spec.get("aviators"):
            for side in (-1, 1):
                c.move_to(side * 14, -448); c.line_to(side * 108, -452)
                c.curve_to(side * 116, -398, side * 88, -366, side * 60, -368)
                c.curve_to(side * 24, -370, side * 10, -410, side * 14, -448); c.close_path()
                g = cairo.LinearGradient(0, -455, 0, -365)
                g.add_color_stop_rgba(0, 0.16, 0.2, 0.26, 1); g.add_color_stop_rgba(1, 0.05, 0.06, 0.08, 1)
                c.set_source(g); c.fill_preserve()
                setc(c, INK); c.set_line_width(11); c.stroke_preserve()
                setc(c, GOLD); c.set_line_width(5); c.stroke()
                limb(c, [(side * 40, -430), (side * 70, -405)], 6, hexc("#FFFFFF", 0.55))
            c.move_to(-14, -446); c.curve_to(-6, -458, 6, -458, 14, -446)
            setc(c, GOLD); c.set_line_width(6); c.stroke()
            for side in (-1, 1):
                limb(c, [(side * 108, -450), (side * 150, -440)], 4, GOLD)
        if spec.get("shades"):
            for side in (-1, 1):
                rrect(c, side * 60 - 52, -455, 104, 66, 18); fs(c, INK)
                limb(c, [(side * 60 - 30, -440), (side * 60 - 10, -425)], 6, hexc("#FFFFFF", 0.7))
            limb(c, [(-10, -440), (10, -440)], 6, INK)
            if expr in ("smile", "smug", "happy"):
                sparkles(c, 50, -320, 10, t, n=1)
        if spec.get("halo"):
            ellipse(c, 0, -640 + 8 * math.sin(t * 3), 95, 24)
            setc(c, INK); c.set_line_width(22); c.stroke_preserve(); setc(c, GOLD); c.set_line_width(12); c.stroke()
        if spec.get("crown"):
            crown(c, 0, -560, 1.1)
        if spec.get("veil"):
            for side in (-1, 1):
                circle(c, side * 80, -528, 18); fs(c, hexc("#F7A8B8"), 5)
        if raised:
            hands = _draw_arms()
        _auto_fx(c, spec, expr, t, seed)
        if extra:
            extra(c)
        if adult:
            c.restore()
        if hold:
            hold(c, hands[1])
        if hold_l:
            hold_l(c, hands[0])


# ---------------------------------------------------------------- cast (archetypes)
HERO = dict(skin="#F1B98C", hair="spiky", hair_c="#3B2416", outfit="shirt", top="#3FA7A0", bottom="#2E3A5C",
            nose="big", logo="J")
GROOM = dict(HERO, outfit="suit", top="#2B2B33", bottom="#2B2B33", logo=None)
BRIDE = dict(skin="#F5CBA7", hair="long", hair_c="#3A2318", outfit="dress", top="#FFFFFF", veil=True, blush=True,
             nose="button")
GOOD_WIFE = dict(skin="#F5CBA7", hair="ponytail", hair_c="#6B3E26", outfit="dress", top="#F4B942", apron=True,
                 blush=True, nose="button", sleeves=True)
BAD_WIFE = dict(skin="#E0A884", hair="bighair", hair_c="#A0412D", outfit="dress", top="#8E44AD", nose="small",
                sleeves=True)
IDEAL = dict(skin="#FBE0B8", hair="wavy", hair_c="#F2C14E", outfit="dress", top="#FFF4D6", trim=True, halo=True,
             wings=True, float=True, blush=True, nose="button")
WOMAN_A = dict(skin="#F5CBA7", hair="bob", hair_c="#2B1A12", outfit="dress", top="#3BAA5C", nose="button")
WOMAN_B = dict(skin="#A86F4C", hair="afro", hair_c="#1E1A1A", outfit="dress", top="#3B6FD1", nose="button")
WOMAN_C = dict(skin="#F8D9BC", hair="ponytail", hair_c="#E2B24A", outfit="dress", top="#E67E22", nose="button")
SHY = dict(skin="#F5CBA7", hair="bangs", hair_c="#2B1A12", outfit="dress", top="#F7A8B8", blush=True, nose="button",
           sleeves=True)
MOTHER = dict(skin="#E8BC98", hair="curlers", hair_c="#C9C9C9", outfit="dress", top="#6D8B74", apron=True,
              glasses=True, nose="small", sleeves=True)
SMART = dict(skin="#F0C8A4", hair="bun", hair_c="#3A2318", outfit="dress", top="#34495E", glasses=True,
             nose="small", sleeves=True)
OLD_HERO = dict(HERO, hair="comb", hair_c="#C9C9C9", moustache=True, top="#5E8C88", logo=None)
GUY_B = dict(HERO, skin="#C98E66", hair="short", hair_c="#1E1A1A", top="#E67E22", nose="small", logo=None)
GUY_C = dict(HERO, skin="#F8D9BC", hair="quiff", hair_c="#D9A441", top="#8E44AD", nose="small", logo=None)
CHAD = dict(skin="#E8AE84", hair="quiff", hair_c="#2B1A12", outfit="suit", top="#1F2A44", bottom="#1F2A44",
            head="square", shades=True, nose="small")
RICH_GUY = CHAD
KID_A = dict(HERO, top="#F5C542", bottom="#3B6FD1", nose="small", logo=None)
KID_B = dict(skin="#F5CBA7", hair="ponytail", hair_c="#3A2318", outfit="dress", top="#F08A8A", blush=True,
             nose="button")


# Bold baby: discipline-mentor attitude in a toddler body -- buzz cut, stubble, furrowed brows, muscles
BOLD_BASE = dict(skin="#E9B48C", hair="buzz", hair_c="#3A2A20", stubble=True, intense=True, baby=True,
                 muscles=True, nose="small")
BOLD_A = dict(BOLD_BASE, outfit="tank", top="#F4F4F2", trim_c="#22305A")              # white tank, navy trim
BOLD_B = dict(BOLD_BASE, outfit="shirt", top="#8E9198", sleeve_c="#3E4149", sleeve_len=0.95, aviators=True)  # raglan + aviators
BOLD_C = dict(BOLD_A, aviators=True)                                                  # tank + aviators


def dumbbell(c, h, t=0.0):
    with xf(c, h[0], h[1], rot=10 * math.sin(t * 4)):
        limb(c, [(-60, 0), (60, 0)], 14, hexc("#9AA5AE"))
        for sx in (-1, 1):
            rrect(c, sx * 62 - 18, -38, 36, 76, 8); fs(c, INK)


def coffee_mug(c, h):
    with xf(c, h[0], h[1] - 30):
        rrect(c, -40, -55, 80, 95, 12); fs(c, hexc("#1E1E24"))
        c.new_path(); c.arc(42, -8, 22, -math.pi / 2, math.pi / 2); setc(c, INK); c.set_line_width(14); c.stroke()
        text(c, "BLACK", 0, 2, 20, WHITE)
        for i in range(2):
            c.move_to(-12 + i * 22, -70); c.curve_to(-22 + i * 22, -95, 0 + i * 22, -105, -10 + i * 22, -130)
        setc(c, hexc("#9AA5AE", 0.8)); c.set_line_width(5); c.stroke()


# Adult hero: bold mentor attitude -- buzz cut, stubble, aviators, raglan henley, big arms (original face)
HERO_ADULT = dict(rig="adult", skin="#E2A57C", hair="buzz", hair_c="#3A2A20", stubble=True, intense=True,
                  head="jaw", nose="small", outfit="shirt", top="#8E9198", sleeve_c="#3B3E46",
                  bottom="#2E3F66", aviators=True)


def gold_person(c, x, y, s=1.0, t=0.0, alpha=1.0, **kw):
    """the Dream Girl: floating angel with halo, wings and golden glow"""
    person(c, x, y, IDEAL, s=s, t=t, alpha=alpha, glow=True, expr=kw.pop("expr", "smile"), **kw)
    sparkles(c, x, y - 320 * s, 320 * s, t, n=7, alpha=alpha)


def stairs_with_crown(c, x, y, s, t):
    """three men on rising steps; Chad (crown, shades) on top"""
    with xf(c, x, y, s=s):
        for i in range(3):
            rrect(c, -330 + i * 220, -i * 120 - 120, 220, i * 120 + 120, 6)
            fs(c, hexc("#E2D6B8"))
        person(c, -220, -120, GUY_C, s=0.42, expr="sad", t=t, blink_seed=3)
        person(c, 0, -240, GUY_B, s=0.42, expr="neutral", t=t, blink_seed=4)
        person(c, 220, -360, dict(CHAD, crown=True), s=0.42, expr="smug", t=t, blink_seed=5,
               arms=(14, 0, 150, -30))
