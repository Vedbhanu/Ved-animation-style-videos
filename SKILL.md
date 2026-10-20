---
name: chaaya-video-youtube
description: Make a vertical (1080x1920) animated psychology / self-improvement / relationships YouTube video or Short in the "Chaaya" style from a pasted script or topic - AI-illustrated sprite cast led by the hero "The Mentor" (buzz cut, aviators, grey raglan), Kokoro am_puck voiceover, comedy SFX, ducked music, punch-ins, impacts, slam text, section colour themes and whip/iris/splat transitions. Scenes are designed fresh for every script (no fixed narrative). Writes image-model prompts for any new characters, cuts the user's generated sheets into sprites, shows stills + a short preview for approval, then renders, and finishes with 3 title options + 3 YouTube thumbnails for the user to pick from (1280x720). Trigger on "Chaaya video", "make a video for this script", "new video like the perfect wife one", "create the next YouTube video", "use the Chaaya video skill", or when the user pastes a script/topic for a cartoon psychology video.
---

# Chaaya video youtube

Turn a script (or topic) into a finished 2–3.5 min vertical cartoon video with the locked Chaaya look.
Video 01 (`videos/01-perfect-wife/`) is the worked example — read its `script.md` and `src/scenes.py` to see
the API used for real, but **never copy its scenes or story order**.

## Paths
- Skill root `SK="$HOME/.claude/skills/chaaya-video-youtube"` (the cloned repo, or a symlink to it).
- `engine/` renderer · `assets/characters/{mentor,cast}/` sprites · `templates/` · `scripts/` · `reference/` · `videos/NN-slug/` projects.
- Run setup first (idempotent): `sh "$SK/scripts/setup.sh"` → prints `PY=` (cairo render python) and `TTS_PY=` (Kokoro).

## Read before planning
1. `reference/style-guide.md` — locked look + editing rules + what must change per video.
2. `reference/characters.md` — every hero/cast pose you can use without new images.
3. `reference/history.md` — scenes already used (vary them).
4. `reference/engine-api.md` — the drawing/animation API and gotchas.
5. `reference/image-prompts.md` — prompt blocks for new characters.
6. `reference/thumbnail-and-title.md` — final step: titles + thumbnails.

## User rules (from the owner — follow strictly)
- **Never soften or censor the script's message.** Keep their wording; they manage platform risk. Cut only for
  length/repetition and say what you cut.
- **No forced formula.** Don't always use "the X Rule" titles or the reference channel's 8-beat story. Pick the
  hook, title and structure that fit THIS script. Add a myth/history frame only when it truly fits.
- Ask per video: **length** (default 2–3 min; sometimes a Short) and **CTA** (book/download link or follow/part 2).
- **Confirm before big steps**: script edit → storyboard → (image prompts) → stills → ~15–45 s preview → full render.

## Workflow

### 1. Script (approval gate)
- Ask length + CTA if not given. At Puck speed ≈ 185 wpm: 2 min ≈ 370 words, 3 min ≈ 555, 3.5 min ≈ 650.
- Create the project: `python3 "$SK/scripts/new_video.py" "<Title>"` → `videos/NN-slug/` with `script.md`,
  `src/scenes.py` (template), `src/score.py` (template).
- Write `script.md`: header (title card lines, CTA) + `---` + one paragraph per beat (each paragraph = one timed
  line `L(i)`; split long paragraphs so each is one visual idea). Write a fresh hook for this script.
- Show the script, title-card text and a one-line note of any cuts. Wait for approval.

### 2. Storyboard (approval gate)
Write `videos/NN-slug/storyboard.md`: a table with one row per shot —
`time/line | what's said (key words) | theme | transition | characters + poses (+ swaps on which word) |
props/graphics | punch/impact/slam | SFX`. Design each beat around the sentence's meaning: a visual metaphor,
a reaction, a number turned into a counter/meter, a list turned into a checklist… (style-guide rules 1–10).
Mark any **missing sprites** (character or pose not in characters.md). Show the storyboard summary.

### 3. New characters/poses (only if needed)
- Write ready-to-paste prompts from `reference/image-prompts.md` (STYLE block + strict 2x4 grid + cream bg +
  numbered order + which reference image to upload). Prefer reusing/re-posing existing cast over new people.
- When the user uploads: convert/upscale into `assets/characters/<set>/src/`, cut with
  `PY engine/cutout.py <src.png> <dir> pose a,b,c,... --grid 2x4`, run `scripts/spritecheck.py`, LOOK at the
  result, fix problems, then add the names to `reference/characters.md` (and `REL` heights in scenes.py).

### 4. Voice + timings
```
TTS_PY "$SK/scripts/tts.py" <proj>        # build/voice.wav + build/lines.json (am_puck, speed 1.12)
sh "$SK/scripts/words.sh" <proj>          # build/words.json (whisper) + prints every word with its time
```
Whisper can merge/split words ("ANDs" → "end", "99.99%" → "99", ".99", "%") — anchor with `at()` on the words it
actually printed. Paragraph starts `L(i)` are exact; word times are ±0.3 s.

### 5. Scenes + score
- Fill `src/scenes.py` from the storyboard: one `@shot` per beat, shots tile the timeline, every event pinned with
  `at()`. Use `hero()/cast()/hface()/gold_person()` + fx/props. Book/logo images go in `<proj>/assets/`.
- Fill `src/score.py` `SECTIONS` (chord mood per section, following the script's emotional arc).
- Stills check: `PY engine/render.py <proj> --still <8–20 times mid-shot>` then
  `PY scripts/stills_grid.py <proj> <sheet.png>` and LOOK: overlaps, cropped text, missing characters,
  text too long, characters covering each other. Fix and re-check.

### 6. Preview (approval gate) → full render
- `PY scripts/scan_frames.py <proj>` (must report no bad frames).
- Preview the first ~15–45 s: `PY engine/render.py <proj> --start 0 --end 30 --out <proj>/renders/preview.mp4`,
  send it, wait for approval/changes.
- Full: `PY engine/render.py <proj> --out "<proj>/renders/<Title> - FINAL.mp4"` (~4–5 min). Check duration,
  `ffmpeg -af volumedetect` (mean ≈ -19.5 dB) and `blackdetect` (0), sample frames into a contact sheet, then send.
- Add a row to `reference/history.md`.

### 7. Titles + thumbnails (always, at the end)
Follow `reference/thumbnail-and-title.md`: write 3 title options and render 3 thumbnail options
(`PY engine/thumbnail.py <proj>/thumbnail/thumb_X.json <proj>/thumbnail/thumb_X.png`) using the video's
characters and its strongest hook/contrast. Save `<proj>/thumbnail/titles.md`, look at the thumbnails,
then send the final video + the 3 thumbnails + the 3 titles together and ask the user to pick one of each. Record the pick in titles.md.

## Changing the locked look
Hero, voice and motion-graphics style are locked. If the user asks to change them, update
`reference/style-guide.md` (and characters.md / setup) so the next video inherits the change.
