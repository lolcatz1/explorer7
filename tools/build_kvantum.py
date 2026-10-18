#!/usr/bin/env python3
"""build_kvantum.py : build/kvantum/Explorer7/ = AeroThemePlasma's Windows7Aero + win7 explorer item views (9-slice <image> elements)"""
import os, re, io, base64, json
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = ROOT + "/build/parts/"; SRC = "/usr/share/Kvantum/Windows7Aero/"
O = ROOT + "/build/kvantum/Explorer7/"; os.makedirs(O, exist_ok=True)
svg = open(SRC + "Windows7Aero.svg").read(); kv = open(SRC + "Windows7Aero.kvconfig").read()

def uri(im):
    b = io.BytesIO(); im.save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
def nine(prefix, im, m, x0, y0):
    """m = left, right, top, bottom; returns svg <image> elements named like kvantum frames"""
    L, R, T, B = m; w, h = im.size; xs = [0, L, w - R, w]; ys = [0, T, h - B, h]
    names = [["topleft", "top", "topright"], ["left", "", "right"], ["bottomleft", "bottom", "bottomright"]]
    out = []
    for j in range(3):
        for i in range(3):
            box = (xs[i], ys[j], xs[i + 1], ys[j + 1])
            if box[2] <= box[0] or box[3] <= box[1]: continue
            n = names[j][i]; pid = prefix + ("-" + n if n else "")
            out.append(f'<image id="{pid}" x="{x0 + box[0] * 2}" y="{y0 + box[1] * 2}" width="{box[2] - box[0]}" height="{box[3] - box[1]}" preserveAspectRatio="none" xlink:href="{uri(im.crop(box))}"/>')
    return out

M = json.load(open(P + "parts.json"))
states = {"focused": "hot", "toggled": "selected", "pressed": "hotselected", "toggled-inactive": "selectednotfocus", "pressed-inactive": "selectednotfocus"}
new = []; y = 2000
# drop the old iview elements: rename their ids so kvantum no longer finds them
svg = re.sub(r'id="((?:iview|scrollslide|sgrip|trough|scarrow|hdr)-[^"]*)"', r'id="old-\1"', svg)
for kst, wst in states.items():
    im = Image.open(f"{P}Explorer__ListView/listitem-{wst}.png"); m = M[f"Explorer::ListView/listitem-{wst}"]["margins"] or [3, 3, 3, 3]
    new += nine("iview-" + kst, im, m, 2000, y); y += 200
# scrollbars (ScrollBar class): kvantum keeps one orientation and rotates it (ORIENT = which win7 set to use)
ORIENT = os.environ.get("SB_ORIENT", "vert")
def sb(name): return Image.open(f"{P}ScrollBar/{name}.png").convert("RGBA")
def stretch_track(im, m, size):
    """make a full-width track tile from the 1px strip: keep the fixed edges, stretch the middle"""
    L, R, T, B = m
    if ORIENT == "horz":
        top, mid, bot = im.crop((0, 0, 1, T)), im.crop((0, T, 1, im.height - B)), im.crop((0, im.height - B, 1, im.height))
        t = Image.new("RGBA", (8, size)); col = Image.new("RGBA", (1, size)); col.paste(top, (0, 0)); col.paste(mid.resize((1, size - T - B)), (0, T)); col.paste(bot, (0, size - B))
        for x in range(8): t.paste(col, (x, 0))
    else:
        l, mid, r = im.crop((0, 0, L, 1)), im.crop((L, 0, im.width - R, 1)), im.crop((im.width - R, 0, im.width, 1))
        t = Image.new("RGBA", (size, 8)); row = Image.new("RGBA", (size, 1)); row.paste(l, (0, 0)); row.paste(mid.resize((size - L - R, 1)), (L, 0)); row.paste(r, (size - R, 0))
        for y in range(8): t.paste(row, (0, y))
    return t
th = "thumbbtnhorz" if ORIENT == "horz" else "thumbbtnvert"; tm = list(M[f"ScrollBar/{th}"]["margins"])
# the bar is exactly as wide as the bitmap (17px), so only the long axis stretches: narrow side slices leave room for the gripper
if ORIENT == "vert": tm[0] = tm[1] = 3
for kst, fr in (("normal", 1), ("focused", 2), ("pressed", 3), ("disabled", 4)):
    new += nine("scrollslide-" + kst, sb(f"{th}-{fr}"), tm, 2600, 2000 + fr * 100)
gp = "gripperhorz.imagefile1" if ORIENT == "horz" else "grippervert.imagefile1"
for kst, fr in (("normal", 1), ("focused", 2), ("pressed", 3), ("disabled", 4)):
    g = sb(f"{gp}-{fr}"); new.append(f'<image id="sgrip-{kst}" x="{2800 + fr * 40}" y="2000" width="{g.width}" height="{g.height}" preserveAspectRatio="none" xlink:href="{uri(g)}"/>')
tr = "lowertrackhorz" if ORIENT == "horz" else "lowertrackvert"; trk = stretch_track(sb(f"{tr}-1"), M[f"ScrollBar/{tr}"]["margins"], 17)
new += nine("trough-normal", trk, [0, 0, 0, 0] if True else None, 3000, 2000)
# arrows: button frame over the track + glyph (frames: up 1-4, down 5-8, left 9-12, right 13-16)
tile = stretch_track(sb(f"{tr}-1"), M[f"ScrollBar/{tr}"]["margins"], 17)
for d, base in (("up", 0), ("down", 4), ("left", 8), ("right", 12)):
    for kst, k in (("normal", 1), ("focused", 2), ("pressed", 3), ("disabled", 4)):
        bg = Image.new("RGBA", (17, 17))
        for i in range(0, 17, tile.width if ORIENT == "horz" else 1): pass
        bg = (tile.resize((17, 17)) if ORIENT == "horz" else tile.resize((17, 17)))
        if (d in ("up", "down")) == (ORIENT == "horz"): bg = bg.transpose(Image.Transpose.TRANSPOSE)
        bg = bg.copy(); bg.alpha_composite(sb(f"arrowbtn-{base + k}"))
        gl = sb(f"arrowbtn.imagefile1-{base + k}"); bg.alpha_composite(gl, ((17 - gl.width) // 2, (17 - gl.height) // 2))
        new.append(f'<image id="scarrow-{d}-{kst}" x="{3100 + base * 30 + k * 20}" y="2000" width="17" height="17" preserveAspectRatio="none" xlink:href="{uri(bg)}"/>')
for old in ("scrollslide", "sgrip", "trough", "scarrow", "slider-normal"):
    pass
# column header (ItemsView::Header HEADERITEM: frames normal / hot / pressed, margins 2,2,9,14)
hm = [2, 2, 2, 2]  # real margins are 2,2,9,14 but kvantum adds frame sizes to the header height; the middle rows are flat
# windows paints the header background (part 0) under the items; the item frames alone are transparent
hbg = Image.open(f"{P}ItemsView__Header/0-1.png").convert("RGBA")
for kst, fr in (("normal", 1), ("focused", 2), ("pressed", 3), ("toggled", 1)):
    it = Image.open(f"{P}ItemsView__Header/headeritem-{fr}.png").convert("RGBA")
    base = Image.new("RGBA", it.size, (255, 255, 255, 255)); base.alpha_composite(hbg.resize(it.size)); base.alpha_composite(it)
    new += nine("hdr-" + kst, base, hm, 3400, 2000 + fr * 60)
new.append('<rect id="iview-normal" x="2400" y="2000" width="8" height="8" style="fill:none;stroke:none"/>')
svg = svg.replace("</svg>", '<g id="explorer7">' + "\n".join(new) + "</g>\n</svg>")
open(O + "Explorer7.svg", "w").write(svg)
kv = re.sub(r"(\[ItemView\][^\[]*?)frame\.top=\d+", r"\1frame.top=3", kv, flags=re.S)
for side in ("bottom", "left", "right"): kv = re.sub(rf"(\[ItemView\][^\[]*?)frame\.{side}=\d+", rf"\1frame.{side}=3", kv, flags=re.S)
def setkv(kv, sec, key, val):
    m = re.search(rf"^\[{re.escape(sec)}\]\n(.*?)(?=^\[|\Z)", kv, re.S | re.M)
    body = m.group(1)
    body = re.sub(rf"^{re.escape(key)}=.*$", f"{key}={val}", body, flags=re.M) if re.search(rf"^{re.escape(key)}=", body, re.M) else body.rstrip("\n") + f"\n{key}={val}\n\n"
    return kv[:m.start(1)] + body + kv[m.end(1):]
L, R, T, B = tm
for k, v in (("frame.left", L), ("frame.right", R), ("frame.top", T), ("frame.bottom", B)): kv = setkv(kv, "ScrollbarSlider", k, v)
kv = setkv(kv, "ScrollbarGroove", "frame", "false")
kv = setkv(kv, "GeneralColors", "alt.base.color", "#ffffff")  # explorer has no row stripes
for k, v in (("frame.left", hm[0]), ("frame.right", hm[1]), ("frame.top", hm[2]), ("frame.bottom", hm[3])): kv = setkv(kv, "HeaderSection", k, v)
for st in ("normal", "focus", "press", "toggle"): kv = setkv(kv, "HeaderSection", f"text.{st}.color", "#4c607a")
open(O + "Explorer7.kvconfig", "w").write(kv)
print("build/kvantum/Explorer7 ready")
