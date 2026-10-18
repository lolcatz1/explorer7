#!/usr/bin/env python3
"""sheet.py <dir> <out.png> [scale] : labelled contact sheet of pngs on a checker background"""
import sys, os, re
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; sc = int(sys.argv[3]) if len(sys.argv) > 3 else 2
fs = sorted([f for f in os.listdir(d) if f.endswith(".png")], key=lambda f: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", f)])
ims = [(f, Image.open(os.path.join(d, f)).convert("RGBA")) for f in fs]
W = 1400; x = y = 0; rowh = 0; pos = []
for f, im in ims:
    w, h = min(im.width * sc, W - 10), min(im.height * sc, 400); w = max(w, 90)
    if x + w > W: x = 0; y += rowh + 18; rowh = 0
    pos.append((f, im, x, y)); x += w + 10; rowh = max(rowh, h)
H = y + rowh + 20; S = Image.new("RGBA", (W, H), (255, 255, 255, 255)); dr = ImageDraw.Draw(S)
for i in range(0, W, 8):
    for j in range(0, H, 8):
        if (i // 8 + j // 8) % 2: dr.rectangle([i, j, i + 7, j + 7], fill=(225, 225, 225, 255))
for f, im, x, y in pos:
    t = im.resize((min(im.width * sc, W - 10), min(im.height * sc, 400)), Image.NEAREST); S.alpha_composite(t, (x, y + 12))
    dr.text((x, y), f.replace(".png", "").replace("bmp_", ""), fill=(200, 0, 0, 255))
S.convert("RGB").save(out); print(out, S.size)
