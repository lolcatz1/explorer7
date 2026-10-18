#!/usr/bin/env python3
"""msstyles.py <aero.msstyles> <outdir> : dump win7 visual style (format per nptr/msstyleEditor libmsstyle, MIT)
outdir/props.json  every property (class, part, state, name, type, value)
outdir/img/<id>.png every IMAGE resource
"""
import sys, os, re, json, struct, pefile
SRC, OUT = sys.argv[1], sys.argv[2]
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ref", "libmsstyle")
os.makedirs(OUT + "/img", exist_ok=True)

# names from libmsstyle's maps
pmap = {int(m.group(1)): m.group(2) for m in re.finditer(r'\{\s*(\d+),\s*new PropertyInfo\("(\w+)"', open(REF + "/VisualStylePropertyMap.cs").read())}
partsrc = open(REF + "/VisualStylePartMap.cs").read()
parts = {}
for m in re.finditer(r'PARTS_(\w+?)(?:_WIN(?:Vista|7|8|81|10|11))?\s*=\s*new List<VisualStylePartEntry>\(\)\s*\{(.*?)\};', partsrc, re.S):
    cls = m.group(1)
    if cls in parts and "_WIN7" not in m.group(0): continue
    parts[cls] = {int(a): b for a, b in re.findall(r'VisualStylePartEntry\((\d+),\s*"(\w+)"', m.group(2))}
TYPES = {200: "ENUM", 201: "STRING", 202: "INT", 203: "BOOL", 204: "COLOR", 205: "MARGINS", 206: "FILENAME", 207: "SIZE", 208: "POSITION", 209: "RECT", 210: "FONT", 211: "INTLIST", 213: "DISKSTREAM", 214: "STREAM", 216: "FLOAT", 240: "COLORLIST", 241: "HCCOLOR"}

pe = pefile.PE(SRC)
res = {}
for t in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    tn = str(t.name) if t.name else str(t.id)
    for e in t.directory.entries:
        en = str(e.name) if e.name else e.id
        d = e.directory.entries[0].data.struct
        res[(tn, en)] = pe.get_memory_mapped_image()[d.OffsetToData:d.OffsetToData + d.Size]
classes = res[("CMAP", "CMAP")].decode("utf-16le").split("\x00")
classes = [c for c in classes if len(c) >= 2]  # libmsstyle numbers only strings of 2+ chars
data = res[("VARIANT", "NORMAL")]

def valid(o):
    if o + 32 > len(data): return False
    n, t, c, p, s, sf, r, sz = struct.unpack_from("<8i", data, o)
    return t in TYPES and 0 <= p < 200 and 0 <= s < 200 and 0 <= c < len(classes) and 0 <= sz < 0x10000

props, o = [], 0
while o + 32 <= len(data):
    if not valid(o): o += 1; continue
    n, t, c, p, s, sf, r, sz = struct.unpack_from("<8i", data, o); o += 32
    v = None; body = data[o:o + sz] if sf == 0 else b""
    if t in (206, 213, 210): v = sf
    elif sf: v = sf
    elif t in (202, 203, 200, 207, 241): v = struct.unpack_from("<i", body)[0] if len(body) >= 4 else 0
    elif t == 204: v = "#%06x" % (struct.unpack_from("<I", body)[0] & 0xffffff) if len(body) >= 4 else None
    elif t in (205, 209): v = list(struct.unpack_from("<4i", body)) if len(body) >= 16 else None
    elif t == 208: v = list(struct.unpack_from("<2i", body)) if len(body) >= 8 else None
    elif t == 201: v = body.decode("utf-16le", "replace").rstrip("\x00")
    elif t == 211: v = list(struct.unpack_from("<%di" % (len(body) // 4), body))[1:] if body else []
    elif t == 240: v = ["#%06x" % (x & 0xffffff) for x in struct.unpack_from("<%dI" % (len(body) // 4), body)]
    elif t == 216: v = struct.unpack_from("<f", body)[0] if len(body) >= 4 else None
    if sf == 0: o += (sz + 7) & ~7
    cname = classes[c] if c < len(classes) else str(c)
    base = cname.split("::")[-1].upper()
    props.append({"class": cname, "part": p, "partName": parts.get(base, {}).get(p, ""), "state": s, "name": pmap.get(n, str(n)), "type": TYPES[t], "value": v})
json.dump(props, open(OUT + "/props.json", "w"), indent=0)
n = 0
for (tn, en), b in res.items():
    if tn == "IMAGE":
        open(f"{OUT}/img/{en}.png", "wb").write(b); n += 1
print(len(classes), "classes,", len(props), "properties,", n, "images")
