"""Image-sprite characters (e.g. AI-generated pose sheets cut out with cutout.py).

    lib = SpriteSet("<dir>")              # loads pose_*.png and face_*.png
    sprite(c, lib.pose["hips"], x, y, h=700, t=t, born=t0)    # feet at (x, y)
    face_card(c, lib.face["shocked"], x, y, size=360, t=t, born=t0)
"""
import glob, math, os
import cairo
from core import *
from chars import squash


class SpriteSet:
    def __init__(self, folder):
        self.pose, self.face = {}, {}
        for f in glob.glob(os.path.join(folder, "*.png")):
            name = os.path.basename(f)[:-4]
            kind, _, key = name.partition("_")
            if kind in ("pose", "face"):
                getattr(self, kind)[key] = cairo.ImageSurface.create_from_png(f)


def sprite(c, surf, x, y, h, t=0.0, born=None, flip=False, bob=True, alpha=1.0, seed=0, shadow=True,
           hop=0.0, rot=0.0):
    """draw an image sprite with its bottom-centre at (x, y), scaled to height h.
    born -> squash & stretch pop-in; bob -> breathing + slight sway; hop -> bounce height (px)."""
    sx, sy = squash(t, born)
    if sx < 0.03 or sy < 0.03:  # degenerate scales make cairo/pixman fail
        return
    iw, ih = surf.get_width(), surf.get_height()
    k = h / ih
    breath = 1 + (0.012 * math.sin(t * 2.6 + seed) if bob else 0)
    sway = (1.2 * math.sin(t * 1.7 + seed) if bob else 0) + rot
    lift = abs(math.sin(t * 9)) * hop
    if shadow:
        with xf(c, x, y):
            ellipse_ = iw * k * 0.36 * sx
            c.save(); c.scale(1, 0.16); c.arc(0, 0, ellipse_, 0, 2 * math.pi); c.restore()
            setc(c, INK[:3] + (0.14 * alpha,)); c.fill()
    c.save()
    c.translate(x, y - lift)
    c.rotate(math.radians(sway))
    c.scale(k * sx * (-1 if flip else 1), k * sy * breath)
    c.set_source_surface(surf, -iw / 2, -ih)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(alpha)
    c.restore()


def face_card(c, surf, x, y, size, t=0.0, born=None, rot=-4.0, col=WHITE):
    """polaroid-style close-up card (like the reference channel's reaction inserts)"""
    sx, sy = squash(t, born, 0.4)
    if sx < 0.03 or sy < 0.03:
        return
    iw, ih = surf.get_width(), surf.get_height()
    with xf(c, x, y, sx=sx, sy=sy, rot=rot + 1.5 * math.sin(t * 2)):
        w, h = size, size * 1.12
        rrect(c, -w / 2 + 14, -h / 2 + 16, w, h, 14); setc(c, INK[:3] + (0.85,)); c.fill()
        rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, col)
        pw, ph = w - 36, w - 36
        px, py = -pw / 2, -h / 2 + 18
        c.save()
        rrect(c, px, py, pw, ph, 8); c.clip()
        setc(c, hexc("#FDE7C8")); c.paint()
        k = max(pw / iw, ph / ih)
        c.translate(px + pw / 2, py + ph)
        c.scale(k, k)
        c.set_source_surface(surf, -iw / 2, -ih)
        c.get_source().set_filter(cairo.FILTER_GOOD)
        c.paint()
        c.restore()
        rrect(c, px, py, pw, ph, 8); fs(c, None, 5)
