#!/usr/bin/env python3
"""build_icons.py : build/icons/Windows 7 Aero/ overlay with explorer's own command bar icons from shell32.dll"""
import os, re, shutil, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC = ROOT + "/build/icons_shell32/"; SYS = "/usr/share/icons/Windows 7 Aero/"
O = ROOT + "/build/icons/Windows 7 Aero/"; shutil.rmtree(O, ignore_errors=True); os.makedirs(O)
MAP = {"view-list-icons": ("actions", 63009), "view-list-details": ("actions", 63011), "view-list-tree": ("actions", 62998),
       "help-contents": ("apps", 24), "documentinfo": ("actions", 16756), "folder-new": ("actions", 319)}
dirs = set(re.findall(r"^\[([^\]]+)\]", open(SYS + "index.theme").read(), re.M))
n = 0
for name, (cat, gid) in MAP.items():
    best = {}
    for f in glob.glob(f"{SRC}{gid}-*.png"):
        w, bpp = re.search(r"-(\d+)x\d+-(\d+)\.png$", f).groups(); w, bpp = int(w), int(bpp)
        if bpp >= best.get(w, (0, ""))[0]: best[w] = (bpp, f)
    for w, (bpp, f) in best.items():
        # every context the system theme has this name in, so ours always wins
        for c in sorted({cat} | {c for c in ("actions", "apps", "places", "status") if glob.glob(f"{SYS}{c}/*/{name}.*")}):
            d = f"{c}/{w}"
            if d not in dirs: continue
            os.makedirs(O + d, exist_ok=True); shutil.copy(f, f"{O}{d}/{name}.png"); n += 1
shutil.copy(SYS + "index.theme", O + "index.theme")
print(n, "icons in build/icons")
