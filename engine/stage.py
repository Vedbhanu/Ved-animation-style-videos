"""Shot timeline: each shot has a time range, a background theme and an entry transition.

    st = Stage()
    @st.shot(t0, t1, theme="gold", trans="whip", sfx=[(t, "pop", 1.0)])
    def my_shot(c, t, lt): ...
    frame, SFX = st.frame, st.sfx
"""
import cairo
from core import W, H, new_frame
from fx import background, transition

TRANS_DUR = {"whip": 0.32, "iris": 0.55, "splat": 0.45, "flip": 0.4, "cut": 0.0}
TRANS_SFX = {"whip": ("swish", 0.9), "iris": ("slide_down", 0.6), "splat": ("splat", 0.9), "flip": ("swish", 0.7)}


class Stage:
    def __init__(self):
        self.shots = []  # (t0, t1, fn, theme, trans)
        self.sfx = []

    def shot(self, t0, t1, theme="cream", trans="whip", sfx=()):
        def deco(fn):
            self.shots.append((t0, t1, fn, theme, trans))
            self.sfx.extend(sfx)
            if self.shots and len(self.shots) > 1 and trans in TRANS_SFX:
                name, g = TRANS_SFX[trans]
                self.sfx.append((t0 - TRANS_DUR[trans] / 2, name, g))
            return fn
        return deco

    def _draw(self, i, t):
        t0, t1, fn, theme, _ = self.shots[i]
        surf, c = new_frame()
        background(c, theme)
        c.save()
        fn(c, t, t - t0)
        c.restore()
        return surf

    def _index(self, t):
        for i, (t0, t1, *_r) in enumerate(self.shots):
            if t0 <= t < t1:
                return i
        return len(self.shots) - 1 if t >= self.shots[-1][1] else 0

    def frame(self, c, t):
        i = self._index(t)
        t0, t1, fn, theme, trans = self.shots[i]
        d = TRANS_DUR.get(trans, 0)
        half = d / 2
        # transition straddles the cut: [t0 - half, t0 + half]
        if i + 1 < len(self.shots):
            n0 = self.shots[i + 1][0]
            nd = TRANS_DUR.get(self.shots[i + 1][4], 0)
            if nd and t >= n0 - nd / 2:
                a = self._draw(i, t)
                b = self._draw(i + 1, t)
                transition(c, self.shots[i + 1][4], a, b, (t - (n0 - nd / 2)) / nd)
                return
        if i > 0 and d and t < t0 + half:
            a = self._draw(i - 1, t)
            b = self._draw(i, t)
            transition(c, trans, a, b, (t - (t0 - half)) / d)
            return
        background(c, theme)
        c.save()
        fn(c, t, t - t0)
        c.restore()
