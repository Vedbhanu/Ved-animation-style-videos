# Image prompts for the user's AI image model

The user generates images manually and uploads them. Give them ready-to-paste prompts built from these
blocks. Always tell them **which reference image to upload** and the **grid order** (we slice by position).

## Rules that make cutting work
- Plain solid cream background `#FDF6DC`, no scenery, no ground, no text/labels/logos/watermarks.
- **Strict grid** (2x4 = 8 per sheet is the sweet spot; 4x4 works but each figure is small), each figure
  alone in an equal cell, full body head-to-feet, lots of empty space between cells, nothing crossing cells.
- Highest resolution the tool allows (each figure ideally ≥ 700 px tall). If they send a small image,
  upscale 2x with ffmpeg lanczos before cutting and mention it.
- Consistency: upload `assets/characters/mentor/src/single_point.png` (hero) or the cast sheet
  (`assets/characters/cast/src/cast_sheet.png`) as the style/character reference.
- Faces of real people: characters may be *inspired by* a public figure's style, but use an original face
  and never their name/logo.

## STYLE block (paste into every prompt)
```
Art style: EXACTLY the same as the reference image — semi-realistic comic illustration (GTA loading-screen
style), bold clean black outlines, cel-shading with one shadow tone, warm orange rim light, expressive slightly
exaggerated faces, appealing and funny. Plain solid cream background (#FDF6DC). No text, no labels, no logos.
```

## A. New cast characters (upload the cast sheet as reference)
```
Character lineup sheet for an animated YouTube explainer series. <STYLE block>
Layout: a strict 2 x 4 grid of 8 separate characters. Each character stands alone in its own equal-sized cell,
full body from head to feet, three-quarter view, centered, lots of empty cream space between cells, no
overlapping, nothing crossing into other cells, no ground scenery.
Row 1:
1. <NAME>: <age/build>, <hair>, <outfit with colours>, <pose>, <expression>.
2. ...
Row 2:
5. ...
All characters share the same line weight, colour saturation, shading and lighting as the reference.
```

## B. Extra poses for existing characters (upload that character's sheet)
```
Same characters as the reference sheet (identical faces, hair, outfits, colours, outlines, rim light).
Pose sheet, strict 2 x 4 grid, each character alone in its own equal cell, full body head to feet, plain cream
background (#FDF6DC), lots of empty space between cells, no overlapping, no text, highest resolution.
1. <CHARACTER>: <pose + expression + prop>.
...
```

## C. Extra hero poses (upload the hero pose sheet `assets/characters/mentor/src/poses2.png`)
```
Same character as the reference image (same face, buzz cut, stubble, gold aviators, grey raglan henley with
charcoal sleeves, blue jeans, brown boots, same art style and rim lighting). Pose sheet, strict 2 x 4 grid,
each pose alone in its own cell, full body, plain cream background (#FDF6DC), lots of space between poses,
no text:
1. <pose> (no sunglasses when the face must act: shocked, crying, love, angry…)
...
```

## D. Hero face close-ups (3x3 grid, head and shoulders)
```
Same character, head and shoulders only, 3x3 grid on plain cream background, same style.
Expressions: <9 expressions>. Same face and buzz cut in every panel. No text.
```

## E. Object / scene sheet (only when a code-drawn prop would look wrong)
```
Prop sheet in the same art style as the reference. Strict 2 x 4 grid, each object alone in its own cell,
centered, plain cream background (#FDF6DC), no text: 1. <object> ...
```
Name them `prop_<name>.png` after cutting (cutout.py prefix `prop`) and draw with `sprite()`.

## Negative prompt (if the tool supports it)
```
text, labels, watermark, logo, overlapping characters, cropped feet, cut-off heads, busy background,
scenery, photorealistic, 3D render, extra limbs, extra fingers, distorted hands, inconsistent style
```

## After the user uploads
```
ffmpeg -i <upload> [-vf scale=iw*2:ih*2:flags=lanczos] assets/characters/<set>/src/<sheet>.png
PY engine/cutout.py <src.png> assets/characters/<set> pose name1,name2,...,name8 --grid 2x4
PY engine/cutout.py <faces.png> assets/characters/mentor face cool,smirk,... --grid 3x3
PY scripts/spritecheck.py assets/characters/<set> <check.png>     # LOOK at it before using
```
cutout.py removes the cream background (border flood fill + enclosed pockets), keeps the largest figure per
panel, crops tight. Check for: leftover cream between legs, pieces of neighbouring cells, holes in white
clothing (lower the pocket threshold `d < 7` if white fabric gets eaten).
Then add the new names to `reference/characters.md`.
