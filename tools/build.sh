#!/bin/sh
# build.sh : iso -> win7 files -> theme parts -> qss + kvantum theme
set -e; ROOT=$(cd "$(dirname "$0")/.." && pwd); PY="$ROOT/.venv/bin/python"; cd "$ROOT"
[ -x "$PY" ] || { python3 -m venv .venv && .venv/bin/pip -q install pefile pillow numpy; }
[ -f build/win7/aero.msstyles ] || tools/extract.sh
$PY tools/msstyles.py build/win7/aero.msstyles build/aero
for f in shellstyle ExplorerFrame; do $PY tools/pe_resources.py build/win7/$f.dll build/$f; done
rm -rf build/parts; $PY tools/export_parts.py
$PY tools/pe_icons.py build/win7/shell32.dll build/icons_shell32 >/dev/null; $PY tools/pe_icons.py build/win7/imageres.dll build/icons_imageres >/dev/null; $PY tools/pe_icons.py build/win7/explorer.exe build/icons_explorer >/dev/null; $PY tools/build_icons.py
$PY tools/build_qss.py; $PY tools/build_kvantum.py
