#!/bin/sh
# dolphin_actions.sh action... : run dolphin on a hidden xvfb display, trigger actions over dbus, quit (state gets saved)
Q=$(command -v qdbus6 || command -v qdbus)
DARGS="$DARGS" xvfb-run -a -s "-screen 0 1024x700x24 -nolisten tcp" sh -c '
  Q=$1; shift
  QT_QPA_PLATFORM=xcb WAYLAND_DISPLAY= dolphin $DARGS --new-window "$HOME" >/dev/null 2>&1 & P=$!
  sleep 5; S=org.kde.dolphin-$P
  for a in "$@"; do $Q $S /dolphin/Dolphin_1 org.kde.KMainWindow.activateAction "$a" >/dev/null && echo "did $a"; sleep 0.3; done
  $Q $S /dolphin/Dolphin_1 org.kde.KMainWindow.activateAction file_quit >/dev/null; sleep 2; kill $P 2>/dev/null' sh "$Q" "$@"
