"""Contact sheet of build/still_*.png. usage: PY stills_grid.py <project> <out.png> [cols=9]"""
import cairo, glob, sys
fs = sorted(glob.glob(sys.argv[1] + "/build/still_*.png"))
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 9
n = len(fs)
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 270 * min(cols, n), 480 * ((n + cols - 1) // cols))
c = cairo.Context(s)
for i, f in enumerate(fs):
    im = cairo.ImageSurface.create_from_png(f)
    c.save(); c.translate((i % cols) * 270, (i // cols) * 480); c.scale(.25, .25); c.set_source_surface(im); c.paint(); c.restore()
s.write_to_png(sys.argv[2])
