# Thumbnail + title (final step of every video)

Reference look: the @Prctical.Psychology channel thumbnails (cream 16:9, hand-lettered or bold caps text,
ONE red keyword, 1–3 characters, sometimes split BEFORE/AFTER with a vertical line and hand-drawn arrows).

## Titles (give exactly 3 options — the user picks one)
Patterns that perform on that channel:
- Curiosity question with a CAPS word: "Why are RICH people GOOD-LOOKING…?", "If looks DON'T matter, why does THIS happen?"
- "If you X, use THIS" / "Use the X Rule" (only when there is a named rule)
- Bold claim / taboo: "At 30, it's already too late!", "Trap for Pretty Women"
- How-to with payoff: "How to make people respect you (without yelling)"
- Test / quiz: "Is your brain intuitive or rational? Take this test"
Rules: ≤ 60 characters where possible, one or two CAPS trigger words, one emoji at the end (🧠 💔 💍 😬 🪤 👀 ⏳),
never clickbait the script doesn't deliver. Keep the user's unsoftened framing.

## Thumbnails (render exactly 3 options, 1280x720 — the user picks one)
`PY engine/thumbnail.py <proj>/thumbnail/thumb_X.json <proj>/thumbnail/thumb_X.png` — see the spec in the
file's docstring. Layouts:
- `text_left` / `text_right`: 2–4 short lines (one in red) + optional small sub-line in brackets; characters
  on the other half (hero reaction pose or face card + the topic's key character), optional light rays.
- `split`: LEFT vs RIGHT headers (BEFORE/NOW, IDEAL/REAL, What distracts you / What you want) + characters
  on each side + x/check badges or arrows + optional bottom title band.
- `title_top`: big title across the top, cast lineup below.
Fonts: `hand` (Chalkboard, mixed case, friendly) or `bold` (Impact caps, punchy). Max ~5 words of big text.
Use the most emotional hero pose (shocked, love, cry, facepalm, point_you) — faces must read at phone size.
Look at the PNGs (contact sheet) before sending; fix overlaps and text touching characters.
Output: `<proj>/thumbnail/thumb_{A,B,C}.png` + `<proj>/thumbnail/titles.md` (3 titles + which thumb pairs with which + the user's final pick).
Make the 3 options genuinely different (e.g. one hand-lettered question, one split contrast, one bold-caps claim).
