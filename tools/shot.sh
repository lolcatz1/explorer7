#!/bin/sh
# shot.sh <name> [dir] [w h] : dolphin alone on a fresh xvfb display -> out/<name>.png
ROOT=$(cd "$(dirname "$0")/.." && pwd); n=$1; dir=${2:-$HOME}; W=${3:-1024}; H=${4:-700}
E7_QSS="$E7_QSS" DOLPHIN="$DOLPHIN" DARGS="$DARGS" xvfb-run -a -s "-screen 0 ${W}x${H}x24 -nolisten tcp" sh -c '
  E7_QSS="$E7_QSS" QT_QPA_PLATFORM=xcb WAYLAND_DISPLAY= ${DOLPHIN:-dolphin} ${DARGS} --new-window "$1" >/dev/null 2>&1 & P=$!
  sleep ${WAIT:-6}; import -window root "$2"; kill $P' sh "$dir" "$ROOT/out/$n.png"
echo "out/$n.png"
