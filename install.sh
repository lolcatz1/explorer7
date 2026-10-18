#!/bin/sh
# install.sh [restore] : explorer 7 look for dolphin (user-local only)
set -e
HERE=$(cd "$(dirname "$0")" && pwd); GV="$HOME/.local/share/dolphin/view_properties/global/.directory"; S="$HOME/.local/share/explorer7"; A="$HOME/.local/share/applications/org.kde.dolphin.desktop"
U="$HOME/.config/systemd/user/plasma-dolphin.service.d/explorer7.conf"; RC="$HOME/.local/share/kxmlgui5/dolphin/dolphinui.rc"
X="$HOME/.local/share/applications/explorer7.desktop"; O="$HOME/.local/opt/dolphin-explorer7"
if [ "$1" = restore ]; then
  # drop the smod exception group install.sh added
  [ -f "$S/smod-group" ] && awk -v g="[Windeco Exception $(cat "$S/smod-group")]" '/^\[/{skip=($0==g)} !skip' "$HOME/.config/smodrc" > "$HOME/.config/smodrc.tmp" && mv "$HOME/.config/smodrc.tmp" "$HOME/.config/smodrc"
  rm -f "$RC" "$A" "$U" "$X" "$HOME/.local/bin/dolphin-explorer7" "$HOME"/.local/share/icons/hicolor/*/apps/explorer7.png; [ -L "$HOME/.local/bin/dolphin" ] && rm -f "$HOME/.local/bin/dolphin"
  [ -f "$HOME/.local/opt/dolphin-explorer7/.from-dist" ] && rm -rf "$HOME/.local/opt/dolphin-explorer7"; rm -rf "$S" "$HOME/.config/Kvantum/Explorer7" "$HOME/.local/share/icons/Windows 7 Aero"
  [ -f "$GV.explorer7" ] && rm -f "$GV" "$GV.explorer7"
  KV="$HOME/.config/Kvantum/kvantum.kvconfig"; [ -f "$KV" ] && kwriteconfig6 --file "$KV" --group Applications --key Explorer7 --delete
  [ -f "$KV" ] && [ ! -s "$KV" ] && rm -f "$KV"
  [ -f "$HOME/.config/dolphinrc.before-explorer7" ] && mv "$HOME/.config/dolphinrc.before-explorer7" "$HOME/.config/dolphinrc"
  [ -f "$HOME/.local/state/dolphinstaterc.before-explorer7" ] && mv "$HOME/.local/state/dolphinstaterc.before-explorer7" "$HOME/.local/state/dolphinstaterc"
  [ -f "$HOME/.config/smodrc.explorer7" ] && rm -f "$HOME/.config/smodrc" "$HOME/.config/smodrc.explorer7"
  qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1
  systemctl --user daemon-reload; kbuildsycoca6 >/dev/null 2>&1; echo restored; exit 0
fi
cp -n "$HOME/.config/dolphinrc" "$HOME/.config/dolphinrc.before-explorer7" 2>/dev/null || true
cp -n "$HOME/.local/state/dolphinstaterc" "$HOME/.local/state/dolphinstaterc.before-explorer7" 2>/dev/null || true
mkdir -p "$S" "$(dirname "$RC")" "$(dirname "$A")" "$(dirname "$U")"
[ -f "$HERE/build/qss/dolphin.qss" ] || { echo "run tools/build.sh first"; exit 1; }
cp "$HERE/src/kxmlgui/dolphinui.rc" "$RC"; rm -rf "$S/img"; cp -r "$HERE/build/qss/img" "$S/img"
sed "s|@IMG@|$S/img|g" "$HERE/build/qss/dolphin.qss" > "$S/dolphin.qss"
# patched dolphin (built by tools/build_dolphin.sh) through a wrapper; the wrapper falls back to /usr/bin/dolphin
mkdir -p "$HOME/.local/bin"; cp "$HERE/tools/dolphin-explorer7.sh" "$HOME/.local/bin/dolphin-explorer7"
sed "s|^Exec=dolphin %u|Exec=$HOME/.local/bin/dolphin-explorer7 %u|" /usr/share/applications/org.kde.dolphin.desktop > "$A"
# prebuilt dolphin from a dist folder; rebuilt from the patch when this system's libraries don't fit
if [ -d "$HERE/opt/dolphin-explorer7" ]; then rm -rf "$O"; mkdir -p "$(dirname "$O")"; cp -r "$HERE/opt/dolphin-explorer7" "$O"; : > "$O/.from-dist"; fi
if [ -x "$O/bin/dolphin" ] && LD_LIBRARY_PATH="$O/lib" ldd "$O/bin/dolphin" | grep -q "not found"; then
  echo "prebuilt dolphin doesn't fit this system's libraries, building from source"
  rm -rf "$O"; "$HERE/tools/build_dolphin.sh" || echo "build failed: the plain system dolphin is used"; fi
[ -x "$O/bin/dolphin" ] || [ -n "$E7_NOBUILD" ] || { echo "building patched dolphin"; "$HERE/tools/build_dolphin.sh" || echo "build failed: the plain system dolphin is used"; }
[ -e "$HOME/.local/bin/dolphin" ] || ln -s dolphin-explorer7 "$HOME/.local/bin/dolphin"
# start menu: "Windows Explorer" next to Dolphin, both open the patched dolphin
sed "s|@BIN@|$HOME/.local/bin/dolphin-explorer7|" "$HERE/src/desktop/explorer7.desktop" > "$X"
for f in "$S"/img/icons/explorer-*.png; do n=${f##*-}; n=${n%.png}; mkdir -p "$HOME/.local/share/icons/hicolor/${n}x$n/apps"; cp "$f" "$HOME/.local/share/icons/hicolor/${n}x$n/apps/explorer7.png"; done
# segoe ui (shipped) unless the system has it
sh "$HERE/tools/get_segoe.sh"
printf '[Service]\nExecStart=\nExecStart=%s/.local/bin/dolphin-explorer7 --daemon\n' "$HOME" > "$U"
[ -d "$HERE/build/kvantum/Explorer7" ] && { rm -rf "$HOME/.config/Kvantum/Explorer7"; mkdir -p "$HOME/.config/Kvantum"; cp -r "$HERE/build/kvantum/Explorer7" "$HOME/.config/Kvantum/Explorer7"
  kwriteconfig6 --file "$HOME/.config/Kvantum/kvantum.kvconfig" --group Applications --key Explorer7 dolphin; }
# explorer's own command bar icons (shell32) as an overlay of the icon theme
[ -d "$HERE/build/icons/Windows 7 Aero" ] && { rm -rf "$HOME/.local/share/icons/Windows 7 Aero"; cp -r "$HERE/build/icons/Windows 7 Aero" "$HOME/.local/share/icons/Windows 7 Aero"; }
# details view by default (only for folders without their own saved view), explorer's columns
if [ ! -f "$GV" ]; then mkdir -p "$(dirname "$GV")"
  printf '[Dolphin]\nViewMode=1\nVersion=4\nVisibleRoles=Details_text,Details_modificationtime,Details_type,Details_size\n' > "$GV"; : > "$GV.explorer7"; fi
kwriteconfig6 --file dolphinrc --group PlacesPanel --key IconSize 16
kwriteconfig6 --file dolphinrc --group DetailsMode --key PreviewSize 16
kwriteconfig6 --file dolphinrc --group Explorer7 --key MenuBar true
kwriteconfig6 --file dolphinrc --group General --key ShowStatusBar 2
kwriteconfig6 --file dolphinrc --group General --key RememberOpenedTabs false
kwriteconfig6 --file dolphinrc --group ContentDisplay --key DirectorySizeMode None
kwriteconfig6 --file dolphinrc --group ContentDisplay --key UseShortRelativeDates false
kwriteconfig6 --file dolphinrc --group DetailsMode --key LeftPadding 4
kwriteconfig6 --file dolphinrc --group DetailsMode --key ExpandableFolders false
kwriteconfig6 --file dolphinrc --group DetailsMode --key RightPadding 4
rm -f "$HOME/.cache/icon-cache.kcache"
kwriteconfig6 --file dolphinrc --group MainWindow --group "Toolbar mainToolBar" --key ToolButtonStyle TextBesideIcon
kwriteconfig6 --file dolphinrc --group MainWindow --group "Toolbar commandBar" --key ToolButtonStyle TextBesideIcon
kwriteconfig6 --file dolphinrc --group MainWindow --group "Toolbar commandBarRight" --key ToolButtonStyle IconOnly
# explorer's caption shows no title or icon (smod decoration exception for dolphin's window class)
if ! grep -q "^ExceptionPattern=dolphin$" "$HOME/.config/smodrc" 2>/dev/null; then
  [ -f "$HOME/.config/smodrc" ] || : > "$HOME/.config/smodrc.explorer7"
  n=0; while grep -q "^\[Windeco Exception $n\]" "$HOME/.config/smodrc" 2>/dev/null; do n=$((n+1)); done; echo "$n" > "$S/smod-group"
  for kv in "ExceptionType 0" "ExceptionPattern dolphin" "Enabled true" "HideIcon true" "HideCaption true" "HideInnerBorder true" "Mask 0"; do
    kwriteconfig6 --file smodrc --group "Windeco Exception $n" --key ${kv%% *} "${kv#* }"; done
  qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1; fi
systemctl --user daemon-reload; kbuildsycoca6 >/dev/null 2>&1
echo "installed; close all dolphin windows and reopen"
