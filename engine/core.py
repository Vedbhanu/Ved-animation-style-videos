"""Core: canvas, colours, timing, primitives, text. Flat webcomic cartoon engine (cream background, thick ink outlines) drawn with Cairo.

Coordinates are in a 1080x1920 portrait canvas. People are drawn with their feet at (x, y);
at s=1 a person is ~520px tall.
"""
import math, random
import cairo

W, H, FPS = 1080, 1920, 30
LW = 7
FONT = "Chalkboard SE"


def hexc(h, a=1.0):
    if isinstance(h, (tuple, list)):
        return tuple(h[:3]) + (a if len(h) < 4 else h[3],)
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


CREAM = hexc("#FDF6DC")
INK = hexc("#1E1A1A")
WHITE = hexc("#FFFFFF")
RED = hexc("#C0392B")
DARKRED = hexc("#A31F1F")
GOLD = hexc("#F5C542")
GREEN = hexc("#3BAA5C")
SKY = hexc("#86D3F5")


# ---------------------------------------------------------------- timing helpers
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def prog(t, t0, dur):
    return clamp((t - t0) / dur) if dur > 0 else float(t >= t0)


def ease_io(p):
    return p * p * (3 - 2 * p)


def ease_out(p):
    return 1 - (1 - p) ** 3


def back(p, k=1.9):
    p -= 1
    return 1 + p * p * ((k + 1) * p + k)


def pop(t, t0, dur=0.32):
    """Scale 0 -> overshoot -> 1. Returns 0 before t0."""
    if t < t0:
        return 0.0
    return back(prog(t, t0, dur))


# ---------------------------------------------------------------- primitives
def setc(c, col):
    c.set_source_rgba(*col)


def fs(c, fill, lw=LW):
    """fill the current path, then outline it in ink"""
    if fill is not None:
        setc(c, fill)
        c.fill_preserve()
    setc(c, INK)
    c.set_line_width(lw)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.stroke()


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()


def circle(c, x, y, r):
    c.new_sub_path()
    c.arc(x, y, r, 0, 2 * math.pi)


def limb(c, pts, width, col):
    """thick outlined stroke (arms, legs, ropes)"""
    for w_, cl in ((width + 2 * LW, INK), (width, col)):
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.set_line_width(w_)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(c, cl)
        c.stroke()


class xf:
    """context manager: translate/scale/rotate around a point, optional alpha group"""

    def __init__(self, c, x=0, y=0, s=1.0, rot=0.0, alpha=1.0, sx=None, sy=None):
        self.c, self.a = c, alpha
        self.args = (x, y, s if sx is None else sx, s if sy is None else sy, rot)

    def __enter__(self):
        c = self.c
        c.save()
        x, y, sx, sy, rot = self.args
        c.translate(x, y)
        if rot:
            c.rotate(math.radians(rot))
        c.scale(sx if abs(sx) > 1e-4 else 1e-4, sy if abs(sy) > 1e-4 else 1e-4)
        if self.a < 1:
            c.push_group()
        return c

    def __exit__(self, *e):
        if self.a < 1:
            self.c.pop_group_to_source()
            self.c.paint_with_alpha(max(self.a, 0))
        self.c.restore()


# ---------------------------------------------------------------- text
def text(c, s, x, y, size, col=INK, bold=True, align="center", outline=None):
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    ext = c.text_extents(s)
    dx = {"center": -ext.width / 2 - ext.x_bearing, "left": -ext.x_bearing, "right": -ext.width - ext.x_bearing}[align]
    c.move_to(x + dx, y)
    c.text_path(s)
    if outline:
        c.set_line_width(outline[1])
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(c, outline[0])
        c.stroke_preserve()
    setc(c, col)
    c.fill()
    return ext.width


def title_card(c, t, line1, line2, t_out=None):
    a = 1.0 if t_out is None else 1 - prog(t, t_out, 0.3)
    if a <= 0:
        return
    with xf(c, 540, 300, s=0.85 + 0.15 * pop(t, 0.0, 0.4), alpha=a):
        text(c, line1, 0, 0, 66)
        text(c, line2, 0, 78, 46, DARKRED, bold=False)


# ---------------------------------------------------------------- frame helpers
def new_frame():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    setc(c, CREAM)
    c.paint()
    return surf, c


def camera(c, zoom=1.0, cx=540, cy=960, dx=0, dy=0):
    c.translate(cx + dx, cy + dy)
    c.scale(zoom, zoom)
    c.translate(-cx, -cy)


