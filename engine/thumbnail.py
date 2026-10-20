"""YouTube thumbnail (1280x720) in the Chaaya style, from a JSON spec.

usage: PY engine/thumbnail.py <spec.json> <out.png>

Spec (all keys optional except layout/lines):
{
  "layout": "text_left" | "text_right" | "split" | "title_top",
  "lines": [["LOOKING FOR THE", "ink"], ["PERFECT", "red"], ["WIFE?", "ink"]],   # (text, ink|red|green|blue)
  "sub": ["(She Doesn't Exist)", "red"],                 # small line under the title
  "font": "hand" | "bold",                                # hand = Chalkboard (lowercase-friendly), bold = Impact caps
  "chars": [{"set": "mentor", "pose": "love", "x": 1010, "y": 700, "h": 620, "flip": false}],
  "faces": [{"face": "shocked", "x": 900, "y": 260, "size": 300, "rot": -4}],
  "split": {"left": ["BEFORE", "red"], "right": ["NOW", "green"]},  # layout=split headers
  "props": [{"kind": "x", "x": 820, "y": 200, "s": 1.0}],  # x | check | heart | arrow | rays | qmark | sparkles
  "arrows": [[[300, 170], [330, 250], [300, 320]]]          # hand-drawn arrows (3 points)
}
"""
import json, math, os, sys
import cairo

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SK, "engine"))
from core import hexc, setc, fs, rrect, poly, circle, xf, INK, RED, GREEN, WHITE, GOLD  # noqa: E402
from props import heart, checkmark, x_badge, question_mark, sparkles  # noqa: E402
from fx import draw_arrow, light_rays  # noqa: E402
from sprites import SpriteSet  # noqa: E402

TW, TH = 1280, 720
COL = {"ink": hexc("#1E1A1A"), "red": hexc("#D0312D"), "green": hexc("#2E9E4F"), "blue": hexc("#2F5FC4"),
       "gold": hexc("#E0A21B")}
FONTS = {"hand": ("Chalkboard SE", cairo.FONT_WEIGHT_BOLD), "bold": ("Impact", cairo.FONT_WEIGHT_NORMAL)}
_SETS = {}


def sset(name):
    if name not in _SETS:
        _SETS[name] = SpriteSet(os.path.join(SK, "assets", "characters", name))
    return _SETS[name]


def paint_sprite(c, surf, x, y, h, flip=False, shadow=True):
    iw, ih = surf.get_width(), surf.get_height()
    k = h / ih
    if shadow:
        c.save(); c.translate(x, y); c.scale(1, 0.16); c.arc(0, 0, iw * k * 0.36, 0, 2 * math.pi); c.restore()
        setc(c, INK[:3] + (0.13,)); c.fill()
    c.save(); c.translate(x, y); c.scale(k * (-1 if flip else 1), k)
    c.set_source_surface(surf, -iw / 2, -ih); c.get_source().set_filter(cairo.FILTER_BEST); c.paint()
    c.restore()


def face_card(c, surf, x, y, size, rot):
    iw, ih = surf.get_width(), surf.get_height()
    with xf(c, x, y, rot=rot):
        w, h = size, size * 1.12
        rrect(c, -w / 2 + 10, -h / 2 + 12, w, h, 12); setc(c, INK[:3] + (0.8,)); c.fill()
        rrect(c, -w / 2, -h / 2, w, h, 12); fs(c, WHITE, 6)
        pw = w - 30
        c.save(); rrect(c, -pw / 2, -h / 2 + 15, pw, pw, 6); c.clip()
        setc(c, hexc("#FDE7C8")); c.paint()
        k = max(pw / iw, pw / ih)
        c.translate(0, -h / 2 + 15 + pw); c.scale(k, k)
        c.set_source_surface(surf, -iw / 2, -ih); c.paint()
        c.restore()


def fit_lines(c, lines, font, box_w, max_size, gap=1.05):
    """largest font size where every line fits box_w"""
    fam, wt = FONTS[font]
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL, wt)
    size = max_size
    while size > 30:
        c.set_font_size(size)
        if all(c.text_extents(t).x_advance <= box_w for t, _ in lines):
            break
        size -= 2
    return size


def draw_lines(c, lines, font, cx, top, box_w, max_size, align="center"):
    fam, wt = FONTS[font]
    size = fit_lines(c, lines, font, box_w, max_size)
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL, wt)
    c.set_font_size(size)
    lh = size * (1.08 if font == "hand" else 1.0)
    y = top + size * 0.85
    for t, col in lines:
        ext = c.text_extents(t)
        x = cx - ext.x_advance / 2 if align == "center" else cx - box_w / 2
        c.move_to(x, y); c.text_path(t)
        c.set_line_width(10); c.set_line_join(cairo.LINE_JOIN_ROUND); setc(c, hexc("#FFF9E8")); c.stroke_preserve()
        setc(c, COL.get(col, INK)); c.fill()
        y += lh
    return y - lh + size * 0.25


def render(spec, out):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, TW, TH)
    c = cairo.Context(surf)
    setc(c, hexc("#FDF6DC")); c.paint()
    g = cairo.RadialGradient(TW / 2, TH / 2, 100, TW / 2, TH / 2, 800)
    g.add_color_stop_rgba(0, 1, 0.98, 0.9, 0.0); g.add_color_stop_rgba(1, 0.93, 0.87, 0.7, 0.35)
    c.set_source(g); c.paint()
    layout = spec.get("layout", "text_left")
    font = spec.get("font", "hand")

    for p in spec.get("props", []):
        if p["kind"] == "rays":
            light_rays(c, p["x"], p["y"], 0.3, p.get("col", "#FFE680"), alpha=p.get("alpha", 0.5), r=p.get("r", 500))

    if layout == "split":
        setc(c, INK); c.set_line_width(5); c.move_to(TW / 2, 0); c.line_to(TW / 2, TH); c.stroke()
        for side, key in ((-1, "left"), (1, "right")):
            lab = spec.get("split", {}).get(key)
            if lab:
                draw_lines(c, [lab], spec.get("split_font", "bold"), TW / 2 + side * TW / 4, 30, TW / 2 - 80, 110)

    for ch in spec.get("chars", []):
        surf_ = sset(ch.get("set", "mentor")).pose[ch["pose"]]
        paint_sprite(c, surf_, ch["x"], ch.get("y", 700), ch.get("h", 600), ch.get("flip", False))
    for f in spec.get("faces", []):
        face_card(c, sset("mentor").face[f["face"]], f["x"], f["y"], f.get("size", 280), f.get("rot", -4))

    for p in spec.get("props", []):
        k, x, y, s = p["kind"], p.get("x", 0), p.get("y", 0), p.get("s", 1.0)
        if k == "x":
            x_badge(c, x, y, s)
        elif k == "check":
            checkmark(c, x, y, s)
        elif k == "heart":
            heart(c, x, y, s)
        elif k == "qmark":
            question_mark(c, x, y, 110 * s, 0.4, col=hexc(p.get("col", "#2F5FC4")))
        elif k == "sparkles":
            sparkles(c, x, y, 150 * s, 0.7, n=6)
    for pts in spec.get("arrows", []):
        draw_arrow(c, [tuple(q) for q in pts], 1.0, col=INK, width=10)

    lines = [tuple(l) for l in spec["lines"]]
    if layout == "text_left":
        cx, top, bw = 330, spec.get("top", 150), 580
    elif layout == "text_right":
        cx, top, bw = 950, spec.get("top", 150), 580
    elif layout == "title_top":
        cx, top, bw = TW / 2, spec.get("top", 25), 1150
    else:  # split: title bottom band
        cx, top, bw = TW / 2, spec.get("top", 560), 1200
    if layout == "split" and lines:
        rrect(c, 0, top - 20, TW, TH - top + 20, 0); setc(c, hexc("#FDF6DC", 0.92)); c.fill()
    bottom = draw_lines(c, lines, font, cx, top, bw, spec.get("max_size", 120))
    if spec.get("sub"):
        st, sc = spec["sub"]
        draw_lines(c, [(st, sc)], "hand", cx, bottom + 15, bw, spec.get("sub_size", 48))
    surf.write_to_png(out)
    print(out)


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
