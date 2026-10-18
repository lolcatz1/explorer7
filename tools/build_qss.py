#!/usr/bin/env python3
"""build_qss.py : build/qss/{dolphin.qss, img/} from the win7 parts (img paths filled in by install.sh: @IMG@)"""
import os, shutil, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = ROOT + "/build/parts/"; O = ROOT + "/build/qss/"
os.makedirs(O + "img", exist_ok=True)
pick = {
  "cm-bg": "CommandModule/modulebackground-1", "cm-hot": "CommandModule/taskbutton-2", "cm-pressed": "CommandModule/taskbutton-3", "cm-focus": "CommandModule/taskbutton-4",
  "cm-menuglyph": "CommandModule/menuglyph-1", "cm-overflow": "CommandModule/overflowglyph-1",
  "ab-1": "AB__AddressBand/background-1", "ab-2": "AB__AddressBand/background-2", "ab-3": "AB__AddressBand/background-3", "ab-4": "AB__AddressBand/background-4",
  "sb-1": "SearchBox/background-1", "sb-2": "SearchBox/background-2", "sb-3": "SearchBox/background-3", "sb-4": "SearchBox/background-4",
}
pick.update({
  "tree-hot": "Explorer__TreeView/treeitem-hot", "tree-selected": "Explorer__TreeView/treeitem-selected",
  "tree-selectednotfocus": "Explorer__TreeView/treeitem-selectednotfocus", "tree-hotselected": "Explorer__TreeView/treeitem-hotselected",
  "tree-glyph-1": "Explorer__TreeView/glyph.imagefile1-1", "tree-glyph-2": "Explorer__TreeView/glyph.imagefile1-2",
  "tree-hotglyph-1": "Explorer__TreeView/hotglyph.imagefile1-1", "tree-hotglyph-2": "Explorer__TreeView/hotglyph.imagefile1-2",
  "details-bg": "PreviewPane/previewbackground-normal",
  "menubar-bg": "ExplorerBar__Rebar/background-1", "menu-item-2": "Menu/baritem-2", "menu-item-3": "Menu/baritem-3", "navpanesizer": "PreviewPane/navpanesizer-1",
  "hdr-sort-1": "ItemsView__Header/headersortarrow.imagefile1-1", "hdr-sort-2": "ItemsView__Header/headersortarrow.imagefile1-2",
  **{f"cm-split-left-{i}": f"CommandModule/splitbuttonleft-{i}" for i in range(1, 6)},
  **{f"cm-split-right-{i}": f"CommandModule/splitbuttonright-{i}" for i in range(1, 6)},
})
for k, v in pick.items(): shutil.copy(P + v + ".png", O + "img/" + k + ".png")
# navigation pane icons (imageres.dll), every size windows ships
import glob, re as _re
NAVICONS = {"favorites": 1024, "libraries": 1023, "desktop": 110, "downloads": 184, "recentplaces": 117, "documents": 1002, "music": 1004,
            "pictures": 1003, "videos": 1005, "homegroup": 1013, "computer": 109, "localdisk": 36, "drive": 32, "removable": 35, "network": 25}
os.makedirs(O + "img/icons", exist_ok=True)
for name, gid in NAVICONS.items():
    best = {}
    for f in glob.glob(f"{ROOT}/build/icons_imageres/{gid}-*.png"):
        w, bpp = map(int, _re.search(r"-(\d+)x\d+-(\d+)\.png$", f).groups())
        if bpp >= best.get(w, (0, ""))[0]: best[w] = (bpp, f)
    for w, (bpp, f) in best.items(): shutil.copy(f, f"{O}img/icons/{name}-{w}.png")
# explorer's own icon (explorer.exe ICO_MYCOMPUTER): the "Open" button for folders
for f in glob.glob(f"{ROOT}/build/icons_explorer/ICO_MYCOMPUTER-*-32.png"):
    w = int(_re.search(r"-(\d+)x\d+-32\.png$", f).group(1)); shutil.copy(f, f"{O}img/icons/explorer-{w}.png")
from PIL import Image; Image.new("RGBA", (1, 1)).save(O + "img/none.png")
# address box glyphs (ExplorerFrame 288: go, stop, refresh, drop-down; 16px each)
ab16 = Image.open(ROOT + "/build/ExplorerFrame/bmp_288.png").convert("RGBA")
ab16.crop((32, 0, 48, 16)).save(O + "img/addr-refresh.png"); ab16.crop((48, 0, 64, 16)).save(O + "img/addr-drop.png")
# back / forward as in explorer: one travel band (ExplorerFrame 280: 4 frames of 70x29 = no history, normal, arrow hot, arrow pressed)
# holding the 27px orb pair (577 normal, 578 hot, 581 pressed, 579 disabled); back = band 0-27, forward = 27-70 (its arrow = recent pages)
EF = ROOT + "/build/ExplorerFrame/"; band = Image.open(EF + "bmp_280.png").convert("RGBA")
fr = lambda i: band.crop((70 * i, 0, 70 * i + 70, 29))
for st, n in (("1", 577), ("2", 578), ("3", 581), ("4", 579)):
    pair = Image.open(f"{EF}bmp_{n}.png").convert("RGBA")
    b = fr(1).crop((0, 0, 27, 29)); b.alpha_composite(pair.crop((0, 0, 27, 27)), (0, 1)); b.save(f"{O}img/back-{st}.png")
    f2 = fr(1).crop((27, 0, 70, 29)); f2.alpha_composite(pair.crop((27, 0, 54, 27)), (0, 1)); f2.save(f"{O}img/fwd-{st}.png")
for st, i in (("2", 2), ("3", 3), ("4", 0)): fr(i).crop((54, 0, 70, 29)).save(f"{O}img/recent-{st}.png")
# travel band widget (patched dolphin): whole band strips + orb pairs at 96 and 120 dpi
shutil.copy(EF + "bmp_280.png", O + "img/band-96.png"); shutil.copy(EF + "bmp_589.png", O + "img/band-120.png")
for st, n96, n120 in (("n", 577, 585), ("h", 578, 586), ("p", 581, 588), ("d", 579, 587)):
    shutil.copy(f"{EF}bmp_{n96}.png", f"{O}img/orbs-{st}-96.png"); shutil.copy(f"{EF}bmp_{n120}.png", f"{O}img/orbs-{st}-120.png")
# address box + refresh box share one border line (AB::AddressBand columns: glow, border, highlight, interior, highlight, border, glow)
for st in ("1", "2", "3", "4"):
    ab = Image.open(f"{P}AB__AddressBand/background-{st}.png").convert("RGBA")
    ab.crop((0, 0, 6, ab.height)).save(f"{O}img/ab-left-{st}.png")
    ab.crop((2, 0, 7, ab.height)).save(f"{O}img/ab-right-{st}.png")
# address icon on search results (imageres 177), breadcrumb overflow chevron «
shutil.copy(f"{ROOT}/build/icons_imageres/177-16x16-32.png", O + "img/addr-search.png")
for st in ("1", "2"): shutil.copy(f"{P}BreadcrumbBar/overflowchevron.glyphimagefile-{st}.png", f"{O}img/crumb-overflow-{st}.png")
# navigation orbs for the travel band widget (aero.msstyles Navigation, 96 / 120 dpi)
for st in ("1", "2", "3", "4"):
    for nm, part in (("nav-back", "backbutton"), ("nav-fwd", "forwardbutton")):
        shutil.copy(f"{P}Navigation/{part}.imagefile1-{st}.png", f"{O}img/{nm}-{st}-96.png")
        shutil.copy(f"{P}Navigation/{part}.imagefile2-{st}.png", f"{O}img/{nm}-{st}-120.png")
# recent pages drop-down: Navigation menubutton widened like explorer does it (22px at 96 dpi), box without the arrow
# (arrow rows inpainted from the column gradient), 4px edges kept, arrow pasted back centred
def menubutton(src_fmt, width, out_fmt):
    arrow = Image.open(src_fmt.format(1)).convert("RGBA")
    mask = [[arrow.getpixel((x, y))[3] > 0 for x in range(arrow.width)] for y in range(arrow.height)]
    for st in ("1", "2", "3", "4"):
        fr = Image.open(src_fmt.format(st)).convert("RGBA"); w, h = fr.size
        box = fr.copy()
        if st in ("2", "3"):
            for x in range(w):
                rows = [y for y in range(h) if mask[y][x]]
                for y in rows:
                    up = next((yy for yy in range(y, -1, -1) if not mask[yy][x]), None)
                    dn = next((yy for yy in range(y, h) if not mask[yy][x]), None)
                    a, b = fr.getpixel((x, up)), fr.getpixel((x, dn))
                    t = (y - up) / (dn - up)
                    box.putpixel((x, y), tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(4)))
        else:
            box = Image.new("RGBA", (w, h))
        e = 4 if w < 15 else 5
        out = Image.new("RGBA", (width, h))
        out.paste(box.crop((0, 0, e, h)), (0, 0))
        mid = box.crop((w // 2, 0, w // 2 + 1, h))
        for x in range(e, width - e): out.paste(mid, (x, 0))
        out.paste(box.crop((w - e, 0, w, h)), (width - e, 0))
        glyph = fr if st in ("1", "4") else arrow
        bb = Image.open(src_fmt.format("1")).getbbox()
        g = glyph.crop((bb[0], 0, bb[2], h))
        out.alpha_composite(g, ((width - g.width) // 2 + 2, 0))
        out.save(out_fmt.format(st))
menubutton(f"{P}Navigation/menubutton.imagefile1-{{}}.png", 22, O + "img/nav-menu-{}-96.png")
menubutton(f"{P}Navigation/menubutton.imagefile2-{{}}.png", 28, O + "img/nav-menu-{}-120.png")
# search box glyphs: magnifier, clear cross, clear cross hot (96 dpi set)
shutil.copy(EF + "bmp_34560.png", O + "img/sb-find.png"); shutil.copy(EF + "bmp_34569.png", O + "img/sb-clear.png"); shutil.copy(EF + "bmp_34572.png", O + "img/sb-clear-hot.png")
M = json.load(open(P + "parts.json")); bg = M["CommandModule/modulebackground"]["margins"]; tb = M["CommandModule/taskbutton"]["margins"]
qss = open(ROOT + "/src/qss/dolphin.qss.in").read()
ab = M["AB::AddressBand/background"]["margins"]; sbm = M["SearchBox/background"]["margins"]
qss = qss.replace("@AB@", f"{ab[2]} {ab[1]} {ab[3]} {ab[0]}").replace("@SB@", f"{sbm[2]} {sbm[1]} {sbm[3]} {sbm[0]}")
# bands whose 9-slice middle is a single row: an exact vertical gradient from the image column instead
def column_gradient(path):
    im = Image.open(path).convert("RGB"); n = im.height
    stops = ", ".join(f"stop:{(y + 0.5) / n:.4f} rgb{im.getpixel((im.width // 2, y))}" for y in range(n))
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, {stops})"
qss = qss.replace("@MENUBAR_GRAD@", column_gradient(P + "ExplorerBar__Rebar/background-1.png"))
qss = qss.replace("@BG@", f"{bg[2]} {bg[1]} {bg[3]} {bg[0]}").replace("@TB@", f"{tb[2]} {tb[1]} {tb[3]} {tb[0]}")
open(O + "dolphin.qss", "w").write(qss); print("build/qss ready")
