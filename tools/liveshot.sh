#!/bin/sh
# liveshot.sh <name> : raise the dolphin window on the real desktop, capture only its rectangle -> out/<name>.png (full capture deleted)
ROOT=$(cd "$(dirname "$0")/.." && pwd); T=${TMPDIR:-/tmp}/explorer7; mkdir -p $T
cat > $T/e7raise.js <<'JS'
let last = null;
for (const w of workspace.windowList()) { if (String(w.resourceClass).indexOf("dolphin") >= 0) last = w; }
if (last) {
  const w = last; w.keepAbove = true; workspace.activeWindow = w;
  if (GEOW > 0) w.frameGeometry = { x: 120, y: 90, width: GEOW, height: GEOH };
  const g = w.frameGeometry; print("E7GEO " + Math.round(g.x) + " " + Math.round(g.y) + " " + Math.round(g.width) + " " + Math.round(g.height));
}
JS
sed -i "s/GEOW/${GEOW:-0}/g; s/GEOH/${GEOH:-0}/g" $T/e7raise.js
n=e7raise$$; id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript $T/e7raise.js $n)
qdbus6 org.kde.KWin /Scripting/Script$id org.kde.kwin.Script.run >/dev/null; sleep 1.5
geo=$(journalctl --user --since "-20s" -o cat | grep E7GEO | tail -1 | cut -d' ' -f2-)
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $n >/dev/null 2>&1
[ -n "$geo" ] || { echo "no dolphin window"; exit 1; }
spectacle -b -n -f -o $T/e7full.png 2>/dev/null; sleep 1.5
"$ROOT/.venv/bin/python" - "$geo" "$ROOT/out/$1.png" "$T/e7full.png" <<'PY'
import sys
from PIL import Image
x, y, w, h = map(int, sys.argv[1].split()); im = Image.open(sys.argv[3]); s = im.width / 1280
im.crop((int(x * s), int(y * s), int((x + w) * s), int((y + h) * s))).save(sys.argv[2])
PY
rm -f $T/e7full.png; echo "out/$1.png ($geo)"
# release keep-above
cat > $T/e7unpin.js <<'JS'
for (const w of workspace.windowList()) { if (String(w.resourceClass).indexOf("dolphin") >= 0) w.keepAbove = false; }
JS
n=e7unpin$$; id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript $T/e7unpin.js $n); qdbus6 org.kde.KWin /Scripting/Script$id org.kde.kwin.Script.run >/dev/null; qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript $n >/dev/null 2>&1
