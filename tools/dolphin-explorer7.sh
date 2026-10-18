#!/bin/sh
# patched dolphin (explorer7) installed under ~/.local/opt; falls back to the system dolphin if missing
P="$HOME/.local/opt/dolphin-explorer7"
[ -x "$P/bin/dolphin" ] || exec /usr/bin/dolphin "$@"
export LD_LIBRARY_PATH="$P/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export QT_PLUGIN_PATH="$P/lib/plugins:$P/lib/qt6/plugins${QT_PLUGIN_PATH:+:$QT_PLUGIN_PATH}"
export XDG_DATA_DIRS="$P/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
exec "$P/bin/dolphin" -stylesheet "${E7_QSS:-$HOME/.local/share/explorer7/dolphin.qss}" "$@"
