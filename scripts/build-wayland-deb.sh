#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME=winvclipboard-wayland
VERSION="${VERSION:-0.2.2~gnome50.1}"
ARCH="$(dpkg --print-architecture)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
STAGE="$WORK/package"
mkdir -p "$ROOT/dist" "$STAGE/DEBIAN"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then PYTHON="$ROOT/venv/bin/python"; fi
"$PYTHON" -m PyInstaller --noconfirm --clean --onedir --name "$NAME" \
    --distpath "$ROOT/dist/wayland-bundle" --workpath "$ROOT/build/wayland" \
    --specpath "$ROOT/build" --hidden-import PySide6.QtDBus "$ROOT/main.py"
install -d "$STAGE/usr/lib/$NAME" "$STAGE/usr/bin"
cp -a "$ROOT/dist/wayland-bundle/$NAME/." "$STAGE/usr/lib/$NAME/"
# GIO loads host modules (GVfs). Use the host GLib family as one consistent ABI.
for library in glib gobject gio gmodule gthread; do
    rm -f "$STAGE/usr/lib/$NAME/_internal/lib${library}-2.0.so"*
done
printf '#!/bin/sh\nexec /usr/lib/winvclipboard-wayland/winvclipboard-wayland "$@"\n' > "$STAGE/usr/bin/$NAME"
chmod 755 "$STAGE/usr/bin/$NAME"
EXT="$STAGE/usr/share/gnome-shell/extensions/winvclipboard-wayland@local"
install -d "$EXT/schemas"
install -m644 "$ROOT/gnome-extension/metadata.json" "$ROOT/gnome-extension/extension.js" "$EXT/"
install -m644 "$ROOT/gnome-extension/schemas/"*.xml "$EXT/schemas/"
glib-compile-schemas --strict "$EXT/schemas"
install -Dm644 "$ROOT/packaging/debian/io.github.winvclipboard.Wayland.desktop" "$STAGE/usr/share/applications/io.github.winvclipboard.Wayland.desktop"
install -Dm644 "$ROOT/packaging/debian/winvclipboard-wayland.desktop" "$STAGE/etc/xdg/autostart/winvclipboard-wayland.desktop"
install -Dm644 "$ROOT/assets/winvclipboard.png" "$STAGE/usr/share/icons/hicolor/256x256/apps/$NAME.png"
install -Dm644 "$ROOT/README.md" "$STAGE/usr/share/doc/$NAME/README.md"
install -Dm644 "$ROOT/packaging/debian/VM-INSTALL.md" "$STAGE/usr/share/doc/$NAME/VM-INSTALL.md"
cp -a "$ROOT/docs" "$STAGE/usr/share/doc/$NAME/docs"
install -m644 "$ROOT/ORIGIN.md" "$ROOT/CHANGELOG.md" "$STAGE/usr/share/doc/$NAME/"
SIZE="$(du -sk "$STAGE/usr" "$STAGE/etc" | awk '{total += $1} END {print total}')"
cat > "$STAGE/DEBIAN/control" <<EOF
Package: $NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: Luthi <luthi@localhost>
Installed-Size: $SIZE
Depends: libc6 (>= 2.39), libstdc++6, libgcc-s1, libglib2.0-0t64, libdbus-1-3, libegl1, libgl1, libopengl0, libfontconfig1, libfreetype6, libxkbcommon0, libwayland-client0, libwayland-cursor0, libwayland-egl1, libxcb-cursor0, libxkbcommon-x11-0, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxcb-render-util0, libxcb-xinerama0, libxcb-xkb1, libx11-6, libxtst6, gnome-shell (>= 50), gnome-shell (<< 51), libglib2.0-bin
Description: Clipboard history and GNOME 50 Wayland companion extension
 Includes a private Python/PySide6 runtime and a GNOME Shell extension.
 Enable the extension per user after installation and logging in again.
 Experimental GNOME 50 integration, with session autostart.
EOF
find "$STAGE" -type d -exec chmod 755 {} +
dpkg-deb --build --root-owner-group -Zxz "$STAGE" "$ROOT/dist/${NAME}_${VERSION}_${ARCH}.deb"
sha256sum "$ROOT/dist/${NAME}_${VERSION}_${ARCH}.deb" > "$ROOT/dist/${NAME}_${VERSION}_${ARCH}.deb.sha256"
printf '\nBuilt: %s\n' "$ROOT/dist/${NAME}_${VERSION}_${ARCH}.deb"
