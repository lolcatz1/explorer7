#!/bin/sh
# explorer7.sh patch | unpatch | status : windows 7 explorer look for dolphin (user-local, reversible)
HERE=$(cd "$(dirname "$0")" && pwd)
O="$HOME/.local/opt/dolphin-explorer7"; S="$HOME/.local/share/explorer7"
I="$HERE/install.sh"; [ -f "$I" ] || I="$HERE/install-linux.sh"

status() {
  if [ -f "$S/dolphin.qss" ] && [ -x "$HOME/.local/bin/dolphin-explorer7" ]; then
    echo "patched$( [ -x "$O/bin/dolphin" ] || echo ' (no patched dolphin)')"
  else
    echo "not patched"
  fi
}

case "$1" in
  patch)   "$I" ;;
  unpatch) "$I" restore ;;
  status)  status ;;
  "")
    echo "explorer7: dolphin as windows 7 explorer"
    echo "now: $(status)"
    printf "1) patch  2) unpatch  3) quit : "
    read c
    case "$c" in 1) "$I" ;; 2) "$I" restore ;; *) exit 0 ;; esac ;;
  *) echo "usage: $0 [patch|unpatch|status]"; exit 1 ;;
esac
