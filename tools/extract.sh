#!/bin/sh
# win7 iso -> build/win7/<files> (only what the look needs; nothing is run)
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd); ISO="$ROOT/downloads/Win7_Ult_SP1_English_x32.iso"; W="$ROOT/build/win7"
echo "65fce0f445d9bf7e78e43f17e441e08c63722657  $ISO" | sha1sum -c --quiet || { echo "iso hash mismatch"; exit 1; }
mkdir -p "$W" "$ROOT/build/tmp"
[ -f "$ROOT/build/tmp/install.wim" ] || 7z e -y -o"$ROOT/build/tmp" "$ISO" sources/install.wim >/dev/null
IDX=$(7z l "$ROOT/build/tmp/install.wim" | awk '/^[0-9-]+ [0-9:]+ D/ && $NF ~ /^[0-9]+$/ {print $NF}' | sort -n | tail -1)
[ -n "$IDX" ] || IDX=1
for f in \
  Windows/Resources/Themes/Aero/aero.msstyles \
  Windows/Resources/Themes/Aero/Shell/NormalColor/shellstyle.dll \
  Windows/System32/ExplorerFrame.dll \
  Windows/System32/en-US/ExplorerFrame.dll.mui \
  Windows/explorer.exe \
  Windows/System32/shell32.dll \
  Windows/System32/en-US/shell32.dll.mui \
  Windows/System32/imageres.dll \
  Windows/Fonts/segoeui.ttf Windows/Fonts/segoeuib.ttf Windows/Fonts/segoeuii.ttf Windows/Fonts/segoeuiz.ttf ; do
  7z e -y -o"$W" "$ROOT/build/tmp/install.wim" "$IDX/$f" >/dev/null && echo "ok  $f" || echo "MISSING $f"
done
