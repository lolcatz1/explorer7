#!/bin/sh
# dist/explorer7-<version>/ + zip for another computer
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd); V=$(cat "$ROOT/VERSION"); D="$ROOT/dist/explorer7-$V"; O="$HOME/.local/opt/dolphin-explorer7"
[ -f "$ROOT/build/qss/dolphin.qss" ] || { echo "run tools/build.sh first"; exit 1; }
[ -x "$O/bin/dolphin" ] || { echo "run tools/build_dolphin.sh first"; exit 1; }
rm -rf "$D"; mkdir -p "$D/build" "$D/src" "$D/tools" "$D/opt"
cp -r "$ROOT/build/qss" "$ROOT/build/kvantum" "$ROOT/build/icons" "$D/build/"
cp -r "$ROOT/src/kxmlgui" "$ROOT/src/desktop" "$D/src/"
cp "$ROOT/tools/dolphin-explorer7.sh" "$ROOT/tools/build_dolphin.sh" "$ROOT/tools/get_segoe.sh" "$D/tools/"
cp -r "$ROOT/patches" "$ROOT/fonts" "$D/"
cp -r "$O" "$D/opt/dolphin-explorer7"; rm -rf "$D/opt/dolphin-explorer7/include" "$D/opt/dolphin-explorer7/lib/cmake" "$D/opt/dolphin-explorer7/.from-dist"
cp "$ROOT/install.sh" "$D/install-linux.sh"; cp "$ROOT/explorer7.sh" "$D/explorer7.sh"
printf '#!/bin/sh\nexec "$(dirname "$0")/install-linux.sh" restore\n' > "$D/uninstall-linux.sh"; chmod +x "$D/uninstall-linux.sh"
cat > "$D/README.txt" <<'TXT'
sh explorer7.sh patch
sh explorer7.sh unpatch
TXT
( cd "$ROOT/dist" && rm -f "explorer7-$V.zip" && 7z a -tzip -bso0 -bsp0 "explorer7-$V.zip" "explorer7-$V" >/dev/null )
echo "dist/explorer7-$V/  and  dist/explorer7-$V.zip"
