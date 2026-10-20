"""Motion graphics & effects: themed backgrounds, light rays, speed lines, impact bursts, kinetic text,
self-drawing strokes, particles, camera punch/shake, and shot transitions."""
import math, random
import numpy as np
import cairo
from core import *
from props import heart, cash_stack

# ---------------------------------------------------------------- section themes
THEMES = {
    "cream": ("#FDF6DC", "#F6E9C2"),
    "gold": ("#FFF3CF", "#FFD970"),
    "red": ("#FBE3DC", "#F2A08F"),
    "grey": ("#EEEBE4", "#C9C4BA"),
    "blue": ("#E6F2FB", "#9FCBEF"),
    "pink": ("#FDE8EE", "#F5B3C6"),
    "green": ("#E9F7E6", "#A8DCA0"),
    "purple": ("#EFE6FA", "#C7AEEB"),
}
_BG = {}


def _bg_surface(theme):
    if theme in _BG:
        return _BG[theme]
    base, accent = THEMES[theme]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    setc(c, hexc(base)); c.paint()
    g = cairo.RadialGradient(540, 980, 100, 540, 980, 1150)
    a = hexc(accent)
    g.add_color_stop_rgba(0, a[0], a[1], a[2], 0.55)
    g.add_color_stop_rgba(1, a[0], a[1], a[2], 0.0)
    c.set_source(g); c.paint()
    # halftone dots, denser toward the corners
    setc(c, hexc(accent, 0.35))
    for yy in range(0, H + 40, 40):
        for xx in range(0, W + 40, 40):
            d = math.hypot(xx - 540, yy - 980) / 1100
            r = 2 + 7 * clamp(d - 0.35)
            if r > 2.2:
                circle(c, xx + (20 if (yy // 40) % 2 else 0), yy, r)
    c.fill()
    _BG[theme] = surf
    return surf


def background(c, theme="cream"):
    c.save(); c.identity_matrix()
    c.set_source_surface(_bg_surface(theme), 0, 0); c.paint()
    c.restore()


# ---------------------------------------------------------------- camera helpers
def punch(t, t0, amt=0.18, dur=0.7):
    """quick zoom-in that eases back out"""
    if t < t0:
        return 0.0
    p = prog(t, t0, dur)
    if p < 0.18:
        return amt * ease_out(p / 0.18)
    return amt * (1 - ease_io((p - 0.18) / 0.82)) * 0.6 + amt * 0.4 * (1 - p)


def shake(t, t0, amp=18, dur=0.45):
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    k = 1 - (t - t0) / dur
    return amp * k * math.sin(t * 90), amp * k * math.cos(t * 77)


def cam(c, t, lt, dur, z0=1.0, z1=1.06, focus=(540, 1100), punches=(), shakes=()):
    """zoom around a focus point; punches = [(t0, amt, (fx, fy))]; shakes = [(t0, amp)]"""
    z = z0 + (z1 - z0) * ease_io(clamp(lt / max(dur, 0.1)))
    fx, fy = focus
    for pc in punches:
        k = punch(t, pc[0], pc[1])
        if k > 0 and len(pc) > 2:
            w = clamp(k / pc[1] * 1.4)
            fx += (pc[2][0] - fx) * w
            fy += (pc[2][1] - fy) * w
        z *= 1 + k
    dx = dy = 0.0
    for sh in shakes:
        a, b = shake(t, sh[0], sh[1] if len(sh) > 1 else 18)
        dx += a; dy += b
    c.translate(fx + dx, fy + dy)
    c.scale(z, z)
    c.translate(-fx, -fy)


# ---------------------------------------------------------------- big background effects
def light_rays(c, x, y, t, col="#FFE680", n=16, r=1400, alpha=0.5, speed=0.25):
    col = hexc(col)
    for i in range(n):
        a0 = t * speed + i * 2 * math.pi / n
        c.move_to(x, y)
        c.arc(x, y, r, a0, a0 + math.pi / n)
        c.close_path()
    setc(c, col[:3] + (alpha,)); c.fill()


def speed_lines(c, t, cx=540, cy=960, n=46, alpha=0.55, inner=380):
    rnd = random.Random(int(t * 12))
    setc(c, INK[:3] + (alpha,))
    for i in range(n):
        a = rnd.random() * 2 * math.pi
        r0 = inner + rnd.random() * 200
        r1 = 1500
        w = 4 + rnd.random() * 14
        c.move_to(cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        c.line_to(cx + r1 * math.cos(a + w / 1500), cy + r1 * math.sin(a + w / 1500))
        c.line_to(cx + r1 * math.cos(a - w / 1500), cy + r1 * math.sin(a - w / 1500))
        c.close_path()
    c.fill()


def burst_shape(c, x, y, r, n=14, jag=0.62, rot=0.0, seed=1):
    rnd = random.Random(seed)
    for i in range(2 * n):
        a = rot + i * math.pi / n
        rr = r if i % 2 == 0 else r * (jag + rnd.random() * 0.12)
        (c.move_to if i == 0 else c.line_to)(x + rr * math.cos(a), y + rr * math.sin(a))
    c.close_path()


def impact(c, x, y, t, t0, label="POW!", col="#F5C542", size=200, dur=0.9, txt_col=None):
    """comic starburst with a word; pops in, holds, shrinks away"""
    if t < t0 or t > t0 + dur:
        return
    k = back(clamp((t - t0) / 0.22)) * (1 - ease_io(clamp((t - (t0 + dur - 0.22)) / 0.22)))
    with xf(c, x, y, s=k, rot=-8 + 6 * math.sin(t * 20)):
        burst_shape(c, 0, 0, size * 1.1, seed=3); fs(c, INK, 1)
        burst_shape(c, 0, 0, size, seed=3); fs(c, hexc(col), 8)
        burst_shape(c, 0, 0, size * 0.72, seed=5); setc(c, WHITE[:3] + (0.5,)); c.fill()
        if label:
            fsz = size * 0.48
            c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            c.set_font_size(fsz)
            fsz = min(fsz, fsz * size * 1.45 / max(1, c.text_extents(label).width))
            text(c, label, 0, fsz * 0.36, fsz, txt_col or RED, outline=(INK, 10))


def flash(c, t, t0, dur=0.12, alpha=0.7):
    if t0 <= t < t0 + dur:
        c.save(); c.identity_matrix()
        setc(c, WHITE[:3] + (alpha * (1 - (t - t0) / dur),)); c.paint(); c.restore()


# ---------------------------------------------------------------- kinetic text
def slam(c, label, x, y, size, t, t0, col=INK, bg=None, rot=-3, outline=None, dur=0.32):
    """word slams into place: big -> overshoot -> settle, with a dust ring"""
    if t < t0:
        return
    p = prog(t, t0, dur)
    s = 2.4 - 1.4 * ease_out(p) if p < 1 else 1
    s *= 1 + 0.04 * math.sin(t * 4)
    with xf(c, x, y, s=s, rot=rot * (1 - 0.3 * p)):
        if bg is not None:
            c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            c.set_font_size(size)
            w = c.text_extents(label).width + 70
            h = size * 1.5
            rrect(c, -w / 2 + 12, -h / 2 + 14, w, h, 20); setc(c, INK); c.fill()
            rrect(c, -w / 2, -h / 2, w, h, 20); fs(c, bg)
        text(c, label, 0, size * 0.36, size, col, outline=outline)
    # dust ring
    if 0.25 < p < 1 or (t - t0) < dur + 0.35:
        q = prog(t, t0 + dur * 0.8, 0.35)
        if 0 < q < 1:
            setc(c, INK[:3] + (0.6 * (1 - q),)); c.set_line_width(6)
            for i in range(10):
                a = i * math.pi / 5
                r0 = size * 2.2 + q * size * 1.2
                c.move_to(x + r0 * math.cos(a), y + r0 * 0.45 * math.sin(a))
                c.line_to(x + (r0 + 40) * math.cos(a), y + (r0 + 40) * 0.45 * math.sin(a))
            c.stroke()


def words_in(c, words, x, y, size, t, times, col=INK, gap=18, rot=0, highlight=None, hl_col=None):
    """kinetic line: each word pops in at its own time; `highlight` words get a colour + bigger"""
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    widths = []
    for w in words:
        c.set_font_size(size * (1.2 if highlight and w in highlight else 1))
        widths.append(c.text_extents(w).x_advance)
    total = sum(widths) + gap * (len(words) - 1)
    cx = x - total / 2
    with xf(c, 0, 0, rot=rot):
        for w, wd, t0 in zip(words, widths, times):
            q = pop(t, t0, 0.28)
            if q:
                big = highlight and w in highlight
                with xf(c, cx + wd / 2, y, s=q):
                    text(c, w, 0, 0, size * (1.2 if big else 1), (hl_col or RED) if big else col,
                         outline=(WHITE, 10))
            cx += wd + gap


def title_slam(c, t, line1, line2, t_out=None, y=300):
    a = 1.0 if t_out is None else 1 - prog(t, t_out, 0.3)
    if a <= 0:
        return
    with xf(c, 0, 0, alpha=a):
        q = prog(t, 0.0, 0.35)
        s = 2.0 - 1.0 * ease_out(q)
        with xf(c, 540, y, s=s * (1 + 0.02 * math.sin(t * 5)), rot=-2):
            c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            c.set_font_size(64)
            w = c.text_extents(line1).width + 70
            rrect(c, -w / 2 + 12, -82 + 14, w, 120, 24); setc(c, INK); c.fill()
            rrect(c, -w / 2, -82, w, 120, 24); fs(c, WHITE)
            text(c, line1, 0, -2, 64)
        q2 = pop(t, 0.35, 0.35)
        if q2:
            with xf(c, 540, y + 120, s=q2, rot=2):
                text(c, line2, 0, 0, 58, DARKRED, outline=(WHITE, 10))


# ---------------------------------------------------------------- self-drawing strokes
def _flat_len(c):
    path = c.copy_path_flat()
    L = 0.0
    last = start = None
    for kind, pts in path:
        if kind == cairo.PATH_MOVE_TO:
            last = start = pts
        elif kind == cairo.PATH_LINE_TO:
            L += math.hypot(pts[0] - last[0], pts[1] - last[1]); last = pts
        elif kind == cairo.PATH_CLOSE_PATH and start:
            L += math.hypot(start[0] - last[0], start[1] - last[1]); last = start
    return L


def stroke_on(c, build, p, width=12, col=RED, ink=True):
    """draw a path progressively: build(c) creates the path, p in 0..1"""
    if p <= 0:
        return
    build(c)
    L = _flat_len(c)
    c.new_path()
    for w_, cl in (((width + 10, INK),) if ink else ()) + ((width, col),):
        build(c)
        c.set_dash([L * p, L + 10], 0)
        c.set_line_width(w_); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(c, cl); c.stroke()
    c.set_dash([])


def scribble_circle(c, x, y, rx, ry, p, col=RED, width=10):
    def b(cc):
        n = 80
        for i in range(n + 1):
            a = -math.pi * 0.6 + i / n * 2.25 * math.pi
            k = 1 + 0.06 * math.sin(i * 0.4)
            (cc.move_to if i == 0 else cc.line_to)(x + rx * k * math.cos(a), y + ry * k * math.sin(a))
    stroke_on(c, b, p, width, col, ink=False)


def underline(c, x0, x1, y, p, col=RED, width=12):
    def b(cc):
        cc.move_to(x0, y)
        cc.curve_to(x0 + (x1 - x0) * 0.3, y + 14, x0 + (x1 - x0) * 0.7, y - 10, x1, y + 4)
    stroke_on(c, b, p, width, col, ink=False)


def draw_arrow(c, pts, p, col=RED, width=16):
    """hand-drawn curved arrow through pts (3 points); head appears at the end"""
    (x0, y0), (x1, y1), (x2, y2) = pts

    def b(cc):
        cc.move_to(x0, y0); cc.curve_to(x1, y1, x1, y1, x2, y2)
    stroke_on(c, b, p, width, col)
    if p >= 0.98:
        ang = math.atan2(y2 - y1, x2 - x1)
        with xf(c, x2, y2, rot=math.degrees(ang)):
            poly(c, [(36, 0), (-22, -32), (-22, 32)]); fs(c, col, 6)


def heart_draw(c, x, y, s, p, col=RED, width=12):
    def b(cc):
        cc.move_to(x, y + 40 * s)
        cc.curve_to(x - 90 * s, y - 20 * s, x - 50 * s, y - 90 * s, x, y - 45 * s)
        cc.curve_to(x + 50 * s, y - 90 * s, x + 90 * s, y - 20 * s, x, y + 40 * s)
    stroke_on(c, b, p, width, col)


# ---------------------------------------------------------------- particles
def money_rain(c, t, t0, n=26, seed=2, dur=99):
    if t < t0 or t > t0 + dur:
        return
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.random() * W
        sp = 300 + rnd.random() * 300
        y = -80 + (t - t0) * sp - rnd.random() * 900
        if y < -80 or y > H + 80:
            continue
        with xf(c, x0 + 50 * math.sin((t - t0) * 2 + i), y, rot=25 * math.sin((t - t0) * 3 + i), s=0.8):
            rrect(c, -60, -32, 120, 64, 6); fs(c, hexc("#7CC47F"), 5)
            circle(c, 0, 0, 18); fs(c, hexc("#B8E6B5"), 3)
            text(c, "$", 0, 11, 30, hexc("#1E6B2F"))


def heart_burst(c, x, y, t, t0, n=12, r=360, seed=4, dur=1.2):
    if t < t0 or t > t0 + dur:
        return
    p = prog(t, t0, dur)
    rnd = random.Random(seed)
    for i in range(n):
        a = i * 2 * math.pi / n + rnd.random() * 0.4
        d = r * ease_out(p) * (0.6 + rnd.random() * 0.5)
        with xf(c, x + d * math.cos(a), y + d * math.sin(a) - 80 * p, s=(0.35 + 0.3 * rnd.random()) * (1 - p * 0.6),
                alpha=1 - p ** 2):
            heart(c)


def burst_particles(c, x, y, t, t0, cols=("#F5C542", "#E74C3C", "#3FA7A0"), n=18, r=300, dur=0.7, seed=6):
    if t < t0 or t > t0 + dur:
        return
    p = prog(t, t0, dur)
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.random() * 2 * math.pi
        d = r * ease_out(p) * (0.5 + rnd.random() * 0.6)
        circle(c, x + d * math.cos(a), y + d * math.sin(a), 12 * (1 - p) + 2)
        setc(c, hexc(cols[i % len(cols)])); c.fill()


def soul(c, x, y, t, t0, s=1.0):
    """ghost leaving the body upward"""
    if t < t0:
        return
    p = prog(t, t0, 1.6)
    with xf(c, x + 30 * math.sin(t * 5), y - 320 * ease_out(p), s=s, alpha=0.85 * (1 - p ** 3)):
        c.move_to(-60, 40); c.curve_to(-70, -100, 70, -100, 60, 40)
        for i in range(4):
            c.line_to(60 - (i + 0.5) * 30, 40 - 18 * (i % 2 == 0))
        c.line_to(-60, 40); c.close_path()
        fs(c, hexc("#FFFFFF", 0.9), 5)
        circle(c, -20, -20, 8); circle(c, 20, -20, 8); setc(c, INK); c.fill()


def sweat_flood(c, x, y, t, s=1.0):
    for i in range(6):
        k = ((t * 1.8) + i / 6) % 1
        side = -1 if i % 2 else 1
        with xf(c, x + side * (150 + 60 * k) * s, y - (450 - 200 * k) * s, s=s, alpha=1 - k):
            c.move_to(0, -26); c.curve_to(20, 0, 20, 24, 0, 24); c.curve_to(-20, 24, -20, 0, 0, -26)
            fs(c, hexc("#8FD3F5"), 5)


# ---------------------------------------------------------------- transitions (operate on surfaces)
def _paint(c, surf, dx=0.0, dy=0.0, alpha=1.0, sx=1.0):
    c.save()
    c.identity_matrix()
    c.translate(540 + dx, 960 + dy)
    c.scale(sx, 1)
    c.translate(-540, -960)
    c.set_source_surface(surf, 0, 0)
    c.paint_with_alpha(alpha)
    c.restore()


def transition(c, kind, a, b, p):
    """composite outgoing surface a and incoming surface b at progress p (0..1) onto c"""
    if kind == "whip":
        e = ease_io(p)
        blur = math.sin(math.pi * p)
        _paint(c, a, -W * e)
        _paint(c, b, W * (1 - e))
        for k in (-2, -1, 1, 2):
            o = k * 40 * blur
            _paint(c, a, -W * e + o, 0, 0.16 * blur)
            _paint(c, b, W * (1 - e) + o, 0, 0.16 * blur)
    elif kind == "iris":
        if p < 0.5:
            _paint(c, a)
            r = 1150 * (1 - ease_io(p * 2))
        else:
            _paint(c, b)
            r = 1150 * ease_io(p * 2 - 1)
        c.save(); c.identity_matrix()
        c.rectangle(0, 0, W, H); circle(c, 540, 960, max(r, 0.1))
        c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); setc(c, INK); c.fill(); c.restore()
    elif kind == "splat":
        _paint(c, a)
        rr = 1300 * ease_out(p)
        c.save(); c.identity_matrix()
        rnd = random.Random(9)
        c.new_path()
        circle(c, 540, 960, rr)
        for i in range(12):
            ang = i * math.pi / 6 + rnd.random() * 0.3
            circle(c, 540 + rr * 0.95 * math.cos(ang), 960 + rr * 0.95 * math.sin(ang), rr * (0.18 + 0.1 * rnd.random()))
        c.clip()
        _paint(c, b)
        c.restore()
    elif kind == "flip":
        if p < 0.5:
            _paint(c, a, sx=max(0.001, 1 - ease_io(p * 2)))
        else:
            _paint(c, b, sx=max(0.001, ease_io(p * 2 - 1)))
    else:  # cut
        _paint(c, b if p >= 0.5 else a)


# ---------------------------------------------------------------- hand-drawn line boil (post-process)
_BOIL = []


def _boil_fields(amp=1.6, n=3):
    if _BOIL:
        return _BOIL
    rng = np.random.default_rng(11)
    yy, xx = np.mgrid[0:H, 0:W]
    for i in range(n):
        gx = rng.standard_normal((H // 120 + 2, W // 120 + 2))
        gy = rng.standard_normal((H // 120 + 2, W // 120 + 2))
        # bilinear upsample
        def up(g):
            fy = yy / 120.0; fx = xx / 120.0
            y0 = fy.astype(int); x0 = fx.astype(int)
            ty = fy - y0; tx = fx - x0
            return (g[y0, x0] * (1 - tx) * (1 - ty) + g[y0, x0 + 1] * tx * (1 - ty)
                    + g[y0 + 1, x0] * (1 - tx) * ty + g[y0 + 1, x0 + 1] * tx * ty)
        dx = np.clip(np.rint(up(gx) * amp), -3, 3).astype(np.int32)
        dy = np.clip(np.rint(up(gy) * amp), -3, 3).astype(np.int32)
        _BOIL.append((np.clip(yy + dy, 0, H - 1).astype(np.int32), np.clip(xx + dx, 0, W - 1).astype(np.int32)))
    return _BOIL


def boil(surf, t, fps_boil=8):
    """subtle hand-drawn wobble: displace the frame with one of 3 noise fields, swapped 8x/second"""
    fields = _boil_fields()
    k = int(t * fps_boil) % len(fields)
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    yy, xx = fields[k]
    a[:] = a[yy, xx]
    surf.mark_dirty()
    return surf
