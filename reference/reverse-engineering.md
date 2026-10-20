# Practical Psychology–style video: reverse-engineering and automation plan

Reference: "If You Lack Discipline, Use the Odysseus Rule" (@Prctical.Psychology)

---

## 1. What the reference video is made of

| Element | What I measured |
|---|---|
| Format | Vertical 9:16 (720×1280 source; we'll render at 1080×1920), 30 fps, **4 min 12 s** |
| Pacing | 771 words in 252 s ≈ **183 words per minute**. That's fast and conversational, with almost no dead air. |
| Cuts | Only about 6 hard cuts. The rest is one continuous "canvas": characters and props pop in, slide, swap and zoom on the same cream background. |
| Background | Flat cream (≈ `#FDF6DC`). Most scenes have **no background at all**, only characters and one or two props. Full scenes (sea, ship, rocks) are used only for the main story. |
| Art style | Simple webcomic-style cartoon: thick black outlines, flat colours, no gradients, big expressive faces, blocky bodies |
| Animation | Limited animation: slow push-ins and pans, pose and expression swaps, pop-ins, shakes, small loops (waving, thrashing). No frame-by-frame animation. |
| Visual devices | **Polaroid insert** (close-up inside a white photo frame over the dimmed scene). **Thought cloud** (what a character is imagining). **Golden glow** for temptations and hallucinations. Coloured **music notes** for the sirens' song. A **"You" label** on a blank character so the viewer sees themselves in it. A **black bar** for comedic censoring. |
| Text on screen | Title card at the top in the first few seconds only: "Don't Have Discipline?" in black, with "(Use the Odysseus Rule)" in red below it, in a hand-written font. **No subtitles.** |
| Audio | One male narrator voice that is energetic, a little theatrical and does character voices. Audio drops below −40 dB 43 times, so **there's no continuous music bed**; it's voice plus occasional sound effects. |
| Ending | Book cover ("Chapter 6 of Atomic Habits"), then an illustration, then "Download it for FREE" with a red arrow. This drives viewers to the pinned video (a lead magnet). |

## 2. The script formula (the part that matters most)

The video uses a repeatable 8-beat structure:

1. **Hook and rule name (0–8 s):** a command plus a named "rule". "Tie yourself to the mast. If you lack discipline… the Odysseus Rule will be your salvation."
2. **Story setup:** a famous historical or mythical figure, what they want and the obstacle in their way. The stakes are personal (family and home).
3. **The clever move:** the hero admits a weakness and designs a system around it. This is the lesson, shown through action.
4. **Escalation and cliffhanger:** "it was worse than they expected…" The story stops at its peak.
5. **Open loop:** "But before you hear the ending…" The viewer is told to apply the lesson to their own life. This keeps people watching for the ending.
6. **Proof stack:** 2 short historical examples (Demosthenes, Victor Hugo), then 2 modern ones in the first person ("I struggle with exercise…"; the junk-food fridge). Each is funny and visual.
7. **Call to reflect:** "Who are the sirens in your life? Write it down." This drives comments.
8. **Payoff and CTA:** finish the story, name the source book and chapter, then "first video on my profile, download it free".

Channel-wide title patterns from the Shorts list: "Use the X Rule", "If you X, do THIS", "Why do RICH people…", "THIS is what makes…". They mix capitalised trigger words with one emoji. The biggest hits are a bit provocative (looks, money, relationships, age).

## 3. The automated pipeline

```
Topic ──► [1 Script] ──► [2 Shot list] ──► [3 Voice] ──► [4 Timing] ──► [5 Visuals] ──► [6 Animate + render] ──► [7 Package]
            Claude         Claude JSON      TTS          Whisper        image gen +       Remotion (code)        title, thumbnail,
                                                         word stamps    asset library                            description
```

### Step 1: Script (Claude)
- Input: topic, plus optionally a source book or chapter.
- Output: a script written to the 8-beat formula, sized to the target length (60 s ≈ 180 words, 4 min ≈ 750 words), plus a "named rule" title and a hook.
- I'll show you the script for approval before anything gets generated.

### Step 2: Shot list (Claude → `shots.json`)
- About one shot per sentence (3–5 s each).
- Each shot records: which characters, pose and expression, props, setting (blank cream or a full scene), camera move, and any devices (polaroid, thought cloud, glow, notes, "You" label).

### Step 3: Voice
- Same narrator every time: male, fast (~180 wpm), expressive, with character voices.
- Best option: **ElevenLabs** (or a cloned or custom voice). Free option: a local TTS (Kokoro), but it's less theatrical.

### Step 4: Timing
- Run **Whisper** on the voiceover to get word-level timestamps. Each shot is then pinned to the exact word that triggers it, so pop-ins land on the spoken word.

### Step 5: Visuals (the hardest part, which is keeping characters consistent)
- **Our own style, not a copy:** same genre (flat cartoon, thick outlines, cream background), but our own character designs, so we don't copy their art.
- **Character bible:** design about 4 recurring characters once (the narrator stand-in, the "You" character, a generic historical hero, the temptation/siren character). Each gets a sheet of poses × expressions.
- **Per-video assets:** generate the specific props and scenes with an image model, using the style reference and character sheets for consistency (e.g. Gemini image / GPT-image / Flux with a style LoRA). Cut each asset out as a transparent PNG.
- The asset library grows with every video, so later videos get cheaper and faster.

### Step 6: Animate and render (Remotion, React → MP4)
- Reusable components: `TitleCard`, `PopIn`, `KenBurns`, `Polaroid`, `ThoughtCloud`, `GoldGlow`, `MusicNotes`, `Shake`, `YouLabel`, `BookOutro`, `CTAArrow`.
- Each shot from `shots.json` maps to these components, so the render is fully code-driven and repeatable.
- Sound effects layer: pop, whoosh, rope creak, a splash and so on, triggered by the shot events. No music bed, matching the reference (we can test a quiet one).

### Step 7: Package
- Final 1080×1920 MP4, 3 title options in the channel's style, a description, and a cover frame.

## 4. Build order

1. Lock the **style and characters**: generate the character bible and approve it.
2. Build the **Remotion template** with all the visual-device components.
3. Run **one full video end to end** on your first topic.
4. Turn the whole thing into a reusable **skill**, so the next video is just "make one about X".

## 5. Decisions needed from you

- **Voice:** ElevenLabs (paid, closest match) or free local TTS?
- **Image generation:** which model or API you have access to (Gemini, OpenAI, Flux/Replicate, Midjourney)?
- **Length:** a full 3–4 min like this one, or ~60 s Shorts like most of the channel?
- **CTA/book:** do you have your own lead magnet or book to point to, like their "download it free"?
