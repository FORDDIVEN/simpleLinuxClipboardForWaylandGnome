# Origen y atribución

**simpleLinuxClipboardForWayland / WinV Clipboard Wayland** deriva de
[simpleLinuxClipboard](https://github.com/FORDDIVEN/simpleLinuxClipboard),
creado para Linux/X11 por FORDDIVEN (Luthi).

Este repositorio continúa como proyecto independiente, orientado a GNOME 50
sobre Wayland. Conserva la base Python/PySide6 de interfaz, historial y
persistencia; añade un puente D-Bus, una extensión GNOME y empaquetado propio.
Los módulos `hotkey.py` y `paste.py` conservan el backend X11 heredado para
sesiones X11. No se utilizan para resolver el atajo o pegado en Wayland.

Se conserva el historial Git para mantener la atribución y la procedencia.
El remoto `upstream` apunta al proyecto original; `origin` debe apuntar al
nuevo repositorio al publicarlo.

## Licencia

La copia recibida no incluye un archivo LICENSE con una licencia estándar.
El README original indicaba «De libre uso, sientase libre de modificar o
mejorar el proyecto». Esta reorganización no añade una licencia nueva ni
cambia las condiciones del código heredado. Antes de distribuir como proyecto
con licencia explícita, su titular debe elegirla y añadir el archivo LICENSE.
Las dependencias mantienen sus propias licencias.
