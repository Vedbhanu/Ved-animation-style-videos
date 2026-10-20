# Engine API (engine/)

`from toon import *` in a scenes file gives everything below. Canvas is **1080x1920 portrait, 30 fps**.
Coordinates are pixels; characters/sprites are anchored at their **feet** (x, y). Ground line ≈ y 1680–1800.

## Timeline: `stage.py`
```python
st = Stage(); shot = st.shot
@shot(t0, t1, theme="gold", trans="whip", sfx=[(time, "pow", gain), ...])
def s_name(c, t, lt):   # t = absolute time, lt = time since shot start
    ...
frame, SFX = st.frame, st.sfx      # required module-level names (+ DURATION)
```
- **themes** (section background colour + halftone): `cream gold red grey blue pink green purple`.
- **trans** (entry transition, straddles the cut, auto-adds its swoosh): `whip` (default, motion blur),
  `iris` (cartoon circle), `splat` (ink blob), `flip` (card flip), `cut`.
- Shots must tile the timeline: next shot's t0 = previous t1. Last shot ends at `DURATION + 1`.

## Timing helpers (in the scenes template)
- `at("word", after=t, end=False)` → start time of the first spoken word ≥ `after` (from build/words.json,
  punctuation stripped, case-insensitive). Chain anchors: `at("pick", L(1))`. Numbers: `at("0%")`, `at("99")`.
- `L(i)` → exact start of script paragraph i (from build/lines.json). Shot boundaries use `L(i) - 0.05`.
- `pop(t, t0, dur)` overshoot 0→1, `prog(t, t0, dur)` linear 0→1, `ease_out/ease_io`, `enter(t, t0, x0, x1, dur)`.

## Characters (sprites)
```python
hero(c, pose, x, y, t, s=1.0, born=None, flip=False, hop=0, rot=0)   # MENTOR.pose[pose], 760px * s * REL
cast(c, pose, x, y, t, s=1.0, born=None, flip=False, hop=0)          # CAST.pose[pose], 700px * s * REL
hface(c, face, x, y, size, t, born=None, rot=-4)                      # polaroid close-up card of the hero
gold_person(c, x, y, s, t)                                            # Dream Girl: floating sprite + glow + sparkles
```
- `born=t0` → squash-and-stretch pop-in at t0. **Swap poses on key words** and pass `born=` the swap time so the
  new pose pops. `hop=12` → bouncy walk while you move x with `enter()`. `flip=True` mirrors (make people face each other).
- Every sprite breathes and sways automatically. No lip-sync/blinks: use pose swaps + face cards for acting.
- Pose/face names: see `reference/characters.md`. Add new sprite heights to `REL` when a pose isn't a full
  standing adult (crouch 0.72, kneel 0.8, kids 0.6).
- Low-level: `sprite(c, surf, x, y, h, t, born, flip, bob, alpha, seed, shadow, hop, rot)`,
  `face_card(c, surf, x, y, size, t, born, rot)`, `SpriteSet(folder)` (loads `pose_*.png`, `face_*.png`).

## Camera & impact (fx.py)
- `cam(c, t, lt, dur, z0=1, z1=1.06, focus=(x,y), punches=[(t0, amt, (fx,fy))], shakes=[(t0, amp)])` —
  call first in every shot. Slow push-in + punch-in zooms (0.06–0.25) + screen shakes (10–22).
- `impact(c, x, y, t, t0, label, col, size, dur=0.9|99, txt_col)` comic starburst word (dur=99 = stays).
- `flash(c, t, t0)` white flash frame. `speed_lines(c, t, cx, cy, alpha)` action lines.
- `light_rays(c, x, y, t, col, alpha, r)` rotating rays behind reveals.

## Kinetic text
- `title_slam(c, t, line1, line2, y=290)` hook title (draw with `c.save(); c.identity_matrix()` so the camera never crops it).
- `slam(c, label, x, y, size, t, t0, col, bg, rot)` word card slams in with a dust ring. Max ~22 chars at size 64.
- `text(c, s, x, y, size, col, bold, align, outline=(WHITE, 8))`, `text_card(...)`, `stamp_label(...)`.
- `words_in(c, words, x, y, size, t, times, highlight=[...])` word-by-word line.
- Draw-ons: `underline(c, x0, x1, y, p)`, `scribble_circle(c, x, y, rx, ry, p)`, `draw_arrow(c, (p0,p1,p2), p, col)`,
  `heart_draw(...)`, `stroke_on(c, build_fn, p)` for any path.

## Particles & reactions
`money_rain(c,t,t0)`, `heart_burst(c,x,y,t,t0)`, `burst_particles(c,x,y,t,t0)`, `confetti(c,t,t0)`,
`sparkles(c,x,y,r,t)`, `floating_hearts(...)`(template), `soul(c,x,y,t,t0)` (ghost leaves body),
`sweat_flood(c,x,y,t,s)`, `puff(c,x,y,p,r)` (smoke poof), `big_x(c,x,y,size,p)`, `x_badge`, `checkmark`, `qmarks(...)`(template), `tear`.

## Props (props.py, code-drawn, flat cartoon)
thought_cloud, ring_box, question_mark, magnifier, arch, house(mood=happy|bad), sun, storm_cloud, sign, heart,
trend_arrow, flames, money_bag, cash_stack, paper(label), briefcase, hourglass, book(label), eye_icon,
jester_hat, crown, gauge(value), cobweb, cane, lightbulb, sink, phone, suitcase, speech_bubble, follow_button,
hand_cursor, padlock. Template helpers: bench, rain, box_pile. Write new props as small functions in the
scenes file (outlined shapes: `rrect/poly/circle` then `fs(c, fill_colour)`; thick outlined strokes: `limb`).
Image props (book covers, logos the user supplies): load with `cairo.ImageSurface.create_from_png` (see `book_cover` in video 01).

## Sound
SFX names (sfx.py): pop boing swish whoosh pow stamp ding twinkle sparkle harp cheer ooh gasp sad dun thunder
record_scratch slide_up slide_down buzzer tick register cash splat poof heartbeat.
Music: `src/score.py` (music_lib: pluck arps + bass + drums; mood per section). render.py ducks it under the voice.

## Render
```
PY engine/render.py <proj> --still 2.5 7.6 ...            # PNG stills -> build/still_*.png
PY scripts/stills_grid.py <proj> <out.png>                # contact sheet of those stills
PY engine/render.py <proj> --start 0 --end 20 --out <proj>/renders/preview.mp4
PY scripts/scan_frames.py <proj>                          # draw every frame, report crashes (do before full render)
PY engine/render.py <proj> --out "<proj>/renders/<Title> - FINAL.mp4"     # ~4-5 min for 3.5 min of video
```
Full render = parallel chunks + hand-drawn line wobble + voice/SFX mix + ducked music + limiter.

## Gotchas (learned the hard way)
- A sprite/card drawn at near-zero scale crashes cairo ("out of memory") — `sprite()`/`face_card()` already
  skip scales < 0.03; keep that guard if you write new image drawing code.
- Draw the title (and any HUD) outside the camera transform or punch-ins crop it.
- Impact/slam labels auto-fit their burst, but keep labels short.
- Never `cat > file` without a heredoc in a shell command (it waits on stdin forever).
- Shell `rm` with a variable path is blocked by a safety check — use literal paths or `"${VAR:?}"`.
