#!/bin/sh
# get_segoe.sh : shipped segoe ui (windows 7) into ~/.local/share/fonts/segoe, unless the system has it
HERE=$(cd "$(dirname "$0")/.." && pwd); F="$HOME/.local/share/fonts/segoe"
fc-list | grep -qi "Segoe UI" && { echo "segoe ui: already installed"; exit 0; }
[ -f "$HERE/fonts/segoeui.ttf" ] || { echo "segoe ui: fonts/ missing"; exit 0; }
mkdir -p "$F"; cp "$HERE"/fonts/segoeui*.ttf "$F/"; fc-cache -f >/dev/null 2>&1; echo "segoe ui: installed"
