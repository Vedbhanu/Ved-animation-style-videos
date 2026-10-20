"""Show every PNG in a sprite folder over a checkerboard (reveals cutout problems).
usage: PY spritecheck.py <folder> <out.png>"""
import cairo, glob, sys
fs = sorted(glob.glob(sys.argv[1] + "/*.png"))
W, H = 2400, 1400
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
for y in range(0, H, 40):
    for x in range(0, W, 40):
        c.set_source_rgb(*((0.75, 0.85, 0.95) if (x // 40 + y // 40) % 2 else (0.95, 0.8, 0.8))); c.rectangle(x, y, 40, 40); c.fill()
x = y = 10; rowh = 0
for f in fs:
    im = cairo.ImageSurface.create_from_png(f)
    k = (330 if "pose" in f else 200) / im.get_height()
    w = im.get_width() * k
    if x + w > W:
        x = 10; y += rowh + 10; rowh = 0
    c.save(); c.translate(x, y); c.scale(k, k); c.set_source_surface(im); c.paint(); c.restore()
    x += w + 10; rowh = max(rowh, im.get_height() * k)
s.write_to_png(sys.argv[2])
