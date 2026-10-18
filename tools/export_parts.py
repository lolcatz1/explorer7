#!/usr/bin/env python3
"""export_parts.py : build/aero/props.json + img -> build/parts/<class>/<part>-<frame>.png + parts.json (margins = left, right, top, bottom)"""
import json, os, re, collections
from PIL import Image
import numpy as np
def load(path):
    # aero.msstyles pngs are premultiplied (colour never exceeds alpha): convert to straight alpha
    a = np.asarray(Image.open(path).convert("RGBA")).astype(float); al = a[..., 3:4]
    a[..., :3] = np.where(al > 0, np.clip(a[..., :3] * 255 / np.maximum(al, 1), 0, 255), 0)
    return Image.fromarray(a.round().astype(np.uint8), "RGBA")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = ROOT + "/build/aero"; O = ROOT + "/build/parts"
P = json.load(open(A + "/props.json")); g = collections.defaultdict(dict)
for p in P: g[(p["class"], p["part"], p["partName"])].setdefault(p["state"], {})[p["name"]] = p["value"]
meta = {}
for (cls, part, pname), states in g.items():
    base = states.get(0, {})
    for key in ("IMAGEFILE", "IMAGEFILE1", "IMAGEFILE2", "IMAGEFILE3", "GLYPHIMAGEFILE"):
        rid = base.get(key)
        if not rid or not os.path.exists(f"{A}/img/{rid}.png"): continue
        im = load(f"{A}/img/{rid}.png"); n = max(1, base.get("IMAGECOUNT") or 1)
        if key == "GLYPHIMAGEFILE": n = max(1, base.get("GLYPHIMAGECOUNT") or n)
        horiz = base.get("IMAGELAYOUT") == 1
        fw, fh = (im.width // n, im.height) if horiz else (im.width, im.height // n)
        d = f"{O}/{re.sub(r'[^A-Za-z0-9_.-]', '_', cls)}"; os.makedirs(d, exist_ok=True)
        tag = (pname or str(part)).lower() + ("" if key == "IMAGEFILE" else "." + key.lower())
        for i in range(n):
            box = (i * fw, 0, i * fw + fw, fh) if horiz else (0, i * fh, fw, i * fh + fh)
            im.crop(box).save(f"{d}/{tag}-{i + 1}.png")
        meta[f"{cls}/{tag}"] = {"image": rid, "frames": n, "size": [fw, fh], "margins": base.get("SIZINGMARGINS"), "content": base.get("CONTENTMARGINS"),
                                "colors": {str(s): {k: v for k, v in st.items() if "COLOR" in k} for s, st in states.items() if any("COLOR" in k for k in st)}}
# images set on a single state (list / tree item hot, selected, ...)
SN = {1: "normal", 2: "hot", 3: "selected", 4: "disabled", 5: "selectednotfocus", 6: "hotselected"}
for (cls, part, pname), states in g.items():
    for st, props in states.items():
        rid = props.get("IMAGEFILE")
        if st == 0 or not rid or not os.path.exists(f"{A}/img/{rid}.png"): continue
        d = f"{O}/{re.sub(r'[^A-Za-z0-9_.-]', '_', cls)}"; os.makedirs(d, exist_ok=True)
        tag = f"{(pname or str(part)).lower()}-{SN.get(st, st)}"
        load(f"{A}/img/{rid}.png").save(f"{d}/{tag}.png")
        meta[f"{cls}/{tag}"] = {"image": rid, "frames": 1, "size": list(Image.open(f"{A}/img/{rid}.png").size), "margins": props.get("SIZINGMARGINS"), "content": None, "colors": {}}
json.dump(meta, open(O + "/parts.json", "w"), indent=1)
print(len(meta), "parts")
