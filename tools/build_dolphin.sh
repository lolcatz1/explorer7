#!/bin/sh
# build_dolphin.sh : patched dolphin 26.08.0 -> ~/.local/opt/dolphin-explorer7
set -e; ROOT=$(cd "$(dirname "$0")/.." && pwd); D="$ROOT/dolphin/dolphin-26.08.0"
[ -d "$D" ] || { mkdir -p "$ROOT/dolphin"; cd "$ROOT/dolphin"; curl -sfL -o dolphin.tar.xz https://download.kde.org/stable/release-service/26.08.0/src/dolphin-26.08.0.tar.xz; tar xf dolphin.tar.xz; cd "$D"; git init -q; git add -A; git -c user.name=upstream -c user.email=upstream@localhost commit -qm upstream; git apply "$ROOT/patches/dolphin-explorer7.patch"; }
cd "$D"; [ -d build ] || cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$HOME/.local/opt/dolphin-explorer7" -DBUILD_TESTING=OFF
cmake --build build -j"$(nproc)"; cmake --install build >/dev/null; echo "installed to ~/.local/opt/dolphin-explorer7"
