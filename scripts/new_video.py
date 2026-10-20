"""Scaffold a new video project:  python3 new_video.py "<Title>"  -> videos/NN-slug/ with templates."""
import os, re, shutil, sys
SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
title = sys.argv[1]
vids = os.path.join(SK, "videos")
n = 1 + max([int(d[:2]) for d in os.listdir(vids) if d[:2].isdigit()] or [0])
slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
proj = os.path.join(vids, f"{n:02d}-{slug}")
for sub in ("src", "build", "assets", "renders"):
    os.makedirs(os.path.join(proj, sub), exist_ok=True)
shutil.copy(os.path.join(SK, "templates", "scenes_template.py"), os.path.join(proj, "src", "scenes.py"))
shutil.copy(os.path.join(SK, "templates", "score_template.py"), os.path.join(proj, "src", "score.py"))
shutil.copy(os.path.join(SK, "templates", "script_template.md"), os.path.join(proj, "script.md"))
print(proj)
