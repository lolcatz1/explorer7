#!/usr/bin/env python3
"""pe_icons.py <file.dll> <outdir> [group ids...] : RT_GROUP_ICON -> <id>-<size>.png (every size in the group)"""
import sys, os, struct, io, pefile
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; want = set(sys.argv[3:]); os.makedirs(out, exist_ok=True)
pe = pefile.PE(src); mm = pe.get_memory_mapped_image()
def entries(tid):
    for t in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if t.id == tid:
            for e in t.directory.entries:
                d = e.directory.entries[0].data.struct; yield (str(e.name) if e.name else e.id), mm[d.OffsetToData:d.OffsetToData + d.Size]
icons = dict(entries(3)); n = 0
for gid, g in entries(14):
    if want and str(gid) not in want: continue
    cnt = struct.unpack_from("<HHH", g, 0)[2]
    for i in range(cnt):
        w, h, cc, r, planes, bpp, size, iid = struct.unpack_from("<BBBBHHIH", g, 6 + i * 14)
        data = icons[iid]; w = w or 256; h = h or 256
        if data[:8] == b"\x89PNG\r\n\x1a\n": im = Image.open(io.BytesIO(data))
        else:
            ico = struct.pack("<HHH", 0, 1, 1) + struct.pack("<BBBBHHII", w % 256, h % 256, cc, 0, planes, bpp, len(data), 22) + data
            im = Image.open(io.BytesIO(ico)); im.size  # noqa
        im.convert("RGBA").save(f"{out}/{gid}-{w}x{h}-{bpp}.png"); n += 1
print(n, "icons")
