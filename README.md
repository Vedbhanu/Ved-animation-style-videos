# Ved Animation Style Videos

A [Claude Code](https://claude.com/claude-code) skill that turns a script or topic into a finished **vertical (1080x1920) animated cartoon video** for YouTube Shorts and long-form videos. It's made for psychology, self-improvement and relationship topics in the "Chaaya" style:

- An AI-illustrated sprite cast led by the hero, "The Mentor"
- Kokoro TTS voiceover (voice `am_puck`), generated locally and for free
- Comedy SFX, music generated in code and ducked under the voice, punch-ins, impacts, slam text and whip/iris/splat transitions
- Ends with 3 title options and 3 YouTube thumbnails (1280x720)

Claude asks you to approve each stage: script → storyboard → stills → preview → full render.

---

## Requirements

- **macOS.** The renderer uses the built-in fonts *Chalkboard SE* and *Impact*.
- **Claude Code** installed and logged in: https://claude.com/claude-code
- **Homebrew:** https://brew.sh
- **Python 3.10+** (`python3 --version`)
- About 1 GB of free disk space for the Python environments and the voice model

## Install

### 1. Install the system tools

```bash
brew install git ffmpeg cairo
```

```bash
pip3 install -U openai-whisper
```

(Whisper gives word-level timings. If `pip3` complains about an "externally managed environment", run `brew install pipx && pipx install openai-whisper` instead.)

### 2. Clone the skill into your Claude skills folder

```bash
mkdir -p ~/.claude/skills
```

```bash
git clone https://github.com/Vedbhanu/Ved-animation-style-videos.git ~/.claude/skills/chaaya-video-youtube
```

The folder **must** be named `chaaya-video-youtube`.

### 3. Run the one-time setup

```bash
sh ~/.claude/skills/chaaya-video-youtube/scripts/setup.sh
```

This creates the render environment (pycairo + numpy) and the Kokoro TTS environment in `~/.cache/animated-short/`, and downloads the voice model (~350 MB). When it finishes it prints two lines, `PY=...` and `TTS_PY=...`, which means it worked.

### 4. Start using it

Open Claude Code in any folder (the Code tab in the Claude desktop app, or `claude` in Terminal) and say something like:

> Use the Chaaya video skill — make a 2-minute video for this script: *(paste script)*

or

> Make a Chaaya video about why discipline beats motivation.

Claude walks you through each step. Finished videos are saved in
`~/.claude/skills/chaaya-video-youtube/videos/NN-title/renders/`.

## Updating

```bash
git -C ~/.claude/skills/chaaya-video-youtube pull
```

## What's inside

| Folder | Contents |
|---|---|
| `SKILL.md` | The instructions Claude follows |
| `engine/` | Renderer: drawing, sprites, effects, SFX, music synth, thumbnails |
| `assets/characters/` | Mentor and cast sprites, plus the source sheets they were cut from |
| `reference/` | Style guide, character list, engine API, image prompts, title/thumbnail rules |
| `scripts/` | Setup, TTS, word timing, new-project scaffolding, QA tools |
| `templates/` | Starting files for each new video |
| `videos/` | Two worked examples (script, storyboard, scenes, score, thumbnails) |

## Troubleshooting

- **`ffmpeg missing`**: run `brew install ffmpeg`.
- **`render env broken`**: run `brew install cairo`, delete `~/.cache/animated-short/venv`, then run setup again.
- **The skill doesn't trigger**: check that `~/.claude/skills/chaaya-video-youtube/SKILL.md` exists, then restart Claude Code.
- **New characters**: the skill writes image-model prompts for you. Generate the sheet in your image tool, upload it to Claude, and it will cut the sprites out.
