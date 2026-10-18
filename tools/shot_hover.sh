#!/bin/sh
# shot_hover.sh <name> <x> <y> : dolphin-explorer7 on xvfb with back history (alt+up), mouse resting at x,y -> out/<name>.png
# E7_QSS = a qss with an opaque mainToolBar background, since xvfb has no glass
ROOT=$(cd "$(dirname "$0")/.." && pwd)
E7_QSS="$E7_QSS" xvfb-run -a -s "-screen 0 1024x700x24 -nolisten tcp" sh -c '
  QT_QPA_PLATFORM=xcb WAYLAND_DISPLAY= E7_QSS="$E7_QSS" $HOME/.local/bin/dolphin-explorer7 --new-window "$HOME/Projects" >/dev/null 2>&1 & P=$!
  sleep 6; xdotool mousemove 500 400 click 1 key alt+Up; sleep 1.5; xdotool mousemove $2 $3; sleep 0.3; xdotool mousemove $(($2+1)) $3; sleep 1; import -window root "$1"; kill $P' sh "$ROOT/out/$1.png" "$2" "$3"
echo "out/$1.png"
