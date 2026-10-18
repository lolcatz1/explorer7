#!/usr/bin/env python3
"""pe_resources.py <file.dll> <outdir> : RT_BITMAP -> png (32bpp keeps straight alpha), UIFILE -> text"""
import sys, os, struct, pefile
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
pe = pefile.PE(src); mm = pe.get_memory_mapped_image()
def raw(e):
    d = e.directory.entries[0].data.struct; return mm[d.OffsetToData:d.OffsetToData + d.Size]
def bmp(b):
    hs, w, h, planes, bpp, comp = struct.unpack_from("<IiiHHI", b, 0)
    if bpp == 32 and comp in (0, 3):
        off = hs + (12 if comp == 3 else 0); hh = abs(h); px = b[off:off + w * hh * 4]
        im = Image.frombuffer("RGBA", (w, hh), px, "raw", "BGRA", 0, -1 if h > 0 else 1)
        if max(px[3::4] or b"\0") == 0: im = im.convert("RGB")
        return im
    colors = struct.unpack_from("<I", b, 32)[0] or (1 << bpp if bpp <= 8 else 0)
    off = 14 + hs + colors * 4 + (12 if comp == 3 and hs == 40 else 0)
    import io; return Image.open(io.BytesIO(b"BM" + struct.pack("<IHHI", 14 + len(b), 0, 0, off) + b))
n = 0
for t in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    tn = str(t.name) if t.name else pefile.RESOURCE_TYPE.get(t.id, str(t.id))
    for e in t.directory.entries:
        en = str(e.name) if e.name else str(e.id); b = raw(e)
        if tn == "RT_BITMAP":
            try: bmp(b).save(f"{out}/bmp_{en}.png"); n += 1
            except Exception as ex: print("bmp", en, ex)
        elif tn == "UIFILE":
            txt = b.decode("utf-16le", "replace") if b[1:2] == b"\0" else b.decode("utf-8", "replace")
            open(f"{out}/uifile_{en}.xml", "w").write(txt); n += 1
print(src, n, "resources")
