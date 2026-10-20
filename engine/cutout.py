"""Cut characters out of AI-generated sheets on a flat light background (numpy + cairo only).

usage: python cutout.py <src.png> <out_dir> <prefix> [names comma-separated] [--grid RxC]
Background = anything connected to the image border that is close to the corner colour.
Each separate figure (split by fully-transparent rows/columns) is saved as <prefix>_<name>.png,
cropped tight with a small margin.
"""
import sys
import numpy as np
import cairo


def load(path):
    s = cairo.ImageSurface.create_from_png(path)
    if s.get_format() != cairo.FORMAT_ARGB32:
        s2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, s.get_width(), s.get_height())
        c = cairo.Context(s2); c.set_source_surface(s, 0, 0); c.paint(); s = s2
    s.flush()
    h, w = s.get_height(), s.get_width()
    a = np.ndarray((h, s.get_stride() // 4, 4), np.uint8, s.get_data())[:, :w].copy()
    return a  # BGRA


def save(arr, path):
    h, w = arr.shape[:2]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    buf = np.ndarray((h, s.get_stride() // 4, 4), np.uint8, s.get_data())
    buf[:, :w] = arr
    s.mark_dirty(); s.write_to_png(path)


def remove_bg(a, tol=34, soft=22):
    rgb = a[:, :, :3].astype(np.int32)
    corners = np.array([rgb[2, 2], rgb[2, -3], rgb[-3, 2], rgb[-3, -3]])
    bg = np.median(corners, axis=0)
    d = np.sqrt(((rgb - bg) ** 2).sum(axis=2))
    cand = d < tol
    seen = np.zeros_like(cand)
    seen[0, :] = cand[0, :]; seen[-1, :] = cand[-1, :]; seen[:, 0] = cand[:, 0]; seen[:, -1] = cand[:, -1]
    while True:  # flood fill from the border through background-coloured pixels
        g = seen.copy()
        g[1:] |= seen[:-1]; g[:-1] |= seen[1:]; g[:, 1:] |= seen[:, :-1]; g[:, :-1] |= seen[:, 1:]
        g &= cand
        if (g == seen).all():
            break
        seen = g
    seen |= d < 7           # enclosed pockets (between legs / arms) of near-exact background colour
    alpha = np.where(seen, 0.0, 1.0)
    # soften the 2px rim next to the background by colour distance
    rim = ~seen & (np.roll(seen, 1, 0) | np.roll(seen, -1, 0) | np.roll(seen, 1, 1) | np.roll(seen, -1, 1))
    alpha[rim] = np.clip((d[rim] - tol * 0.5) / soft, 0.25, 1.0)
    out = a.copy().astype(np.float32)
    out[:, :, :3] *= alpha[:, :, None]           # premultiplied for cairo
    out[:, :, 3] = alpha * 255
    return out.astype(np.uint8), alpha > 0.05


def _flood(mask, y, x):
    blob = np.zeros_like(mask); blob[y, x] = True
    while True:
        g = blob.copy()
        g[1:] |= blob[:-1]; g[:-1] |= blob[1:]; g[:, 1:] |= blob[:, :-1]; g[:, :-1] |= blob[:, 1:]
        g[1:, 1:] |= blob[:-1, :-1]; g[:-1, :-1] |= blob[1:, 1:]
        g &= mask
        if (g == blob).all():
            return blob
        blob = g


def main_component(mask):
    """the largest connected blob, searched from seeds nearest the panel centre"""
    h, w = mask.shape
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return mask
    order = np.argsort((ys - h * 0.55) ** 2 + (xs - w / 2) ** 2)
    best, covered = None, np.zeros_like(mask)
    for k in order[:: max(1, len(order) // 400)]:
        if covered[ys[k], xs[k]]:
            continue
        blob = _flood(mask, ys[k], xs[k])
        covered |= blob
        if best is None or blob.sum() > best.sum():
            best = blob
        if best.sum() > 0.5 * mask.sum():
            break
    return best


def spans(occ, min_gap, min_len):
    res, start, gap = [], None, 0
    for i, v in enumerate(occ):
        if v:
            if start is None:
                start = i
            gap = 0
        elif start is not None:
            gap += 1
            if gap >= min_gap:
                if i - gap - start + 1 >= min_len:
                    res.append((start, i - gap + 1))
                start, gap = None, 0
    if start is not None and len(occ) - start >= min_len:
        res.append((start, len(occ)))
    return res


def main():
    src, out, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    names = sys.argv[4].split(",") if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else None
    grid = None
    if "--grid" in sys.argv:
        r, c_ = sys.argv[sys.argv.index("--grid") + 1].split("x"); grid = (int(r), int(c_))
    a = load(src)
    img, mask = remove_bg(a)
    H, W = mask.shape
    panels = []
    if grid:
        for r in range(grid[0]):
            for c_ in range(grid[1]):
                panels.append((r * H // grid[0], (r + 1) * H // grid[0], c_ * W // grid[1], (c_ + 1) * W // grid[1]))
    else:
        panels = [(0, H, 0, W)]
    for i, (y0, y1, x0, x1) in enumerate(panels):
        sub = main_component(mask[y0:y1, x0:x1])
        piece = img[y0:y1, x0:x1].copy()
        piece[~sub] = 0
        ys, xs = np.where(sub.sum(1) > 0)[0], np.where(sub.sum(0) > 0)[0]
        m = 6
        ya, yb = max(0, ys[0] - m), min(sub.shape[0], ys[-1] + 1 + m)
        xa, xb = max(0, xs[0] - m), min(sub.shape[1], xs[-1] + 1 + m)
        name = names[i] if names and i < len(names) else str(i)
        save(piece[ya:yb, xa:xb], f"{out}/{prefix}_{name}.png")
        print(f"{prefix}_{name}: {xb - xa}x{yb - ya}")


if __name__ == "__main__":
    main()
