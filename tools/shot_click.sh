#!/bin/sh
# shot_click.sh <name> <x> <y> : dolphin on xvfb, click at x,y, screenshot -> out/<name>.png
ROOT=$(cd "$(dirname "$0")/.." && pwd)
xvfb-run -a -s "-screen 0 1024x700x24 -nolisten tcp" sh -c '
  QT_QPA_PLATFORM=xcb WAYLAND_DISPLAY= $HOME/.local/bin/dolphin-explorer7 --new-window "$HOME" >/dev/null 2>&1 & P=$!
  sleep 6; xdotool mousemove $2 $3 click 1; sleep 1.5; import -window root "$1"; kill $P' sh "$ROOT/out/$1.png" "$2" "$3"
echo "out/$1.png"
