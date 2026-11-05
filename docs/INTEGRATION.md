# Integración GNOME Wayland

## Por qué una extensión

GNOME admite el portal GlobalShortcuts desde GNOME 48: https://release.gnome.org/48/developers/ . No sería correcto afirmar que GNOME 50 carece de él. Permite sesiones y señales de activación con autorización del usuario: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html .

Para el flujo completo hacen falta además acceso al portapapeles en segundo plano, control de foco, pegado y restauración de posición. RemoteDesktop permite entrada de teclado en una sesión autorizada; Clipboard está asociado a esa sesión, no es un permiso independiente para observar libremente el escritorio:

- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Clipboard.html

Se eligió un único puente de GNOME para esas cuatro funciones, en lugar de mantener una sesión RemoteDesktop para un gestor de historial. No se implementó un segundo backend de portales. Qt/XWayland no elimina estas restricciones. La extensión utiliza `Meta.Selection`, `Meta.Window`, dispositivos virtuales de Clutter y `Main.wm.addKeybinding`; son APIs específicas de Shell/Mutter y deben verificarse al cambiar GNOME.

## Uso y datos separados

```bash
venv/bin/python main.py
venv/bin/python main.py --toggle
venv/bin/python main.py --show
venv/bin/python main.py --hide
venv/bin/python main.py --quit
```

Los comandos siguen disponibles para automatización. `--hide` y `--quit` sin instancia no inician otra. Arrastra el título del panel para moverlo mediante el compositor. La extensión guarda las coordenadas al terminar el movimiento y las restaura al mostrar o reiniciar; limita la posición al área disponible si cambia el monitor.

- Historial/configuración: `~/.local/share/winvclipboard-wayland/`.
- Imágenes: `~/.cache/winvclipboard-wayland/`.
- Overrides de pruebas: `WINVCLIPBOARD_WAYLAND_DATA_DIR`, `WINVCLIPBOARD_WAYLAND_CACHE_DIR`.
- IPC: `$XDG_RUNTIME_DIR/winvclipboard-wayland-UID/control.sock`, o directorio privado equivalente en `/tmp`.
- Identidad Qt/D-Bus: `io.github.winvclipboard.Wayland`; puente Shell: la misma más `.Shell`.

No se importan ni modifican datos de la variante X11. Historial y configuración se escriben con temporal, fsync y reemplazo atómico. El historial contiene información sensible en texto plano; no hay cifrado ni filtro por aplicación.

## Límites actuales

En Wayland se desactiva la observación Qt global y se usa el puente. Sin extensión no habrá captura en segundo plano, atajo integrado, restauración de posición ni pegado automático; la interfaz y el historial siguen disponibles, y seleccionar copia mediante Qt para pegar manualmente. El backend XTest nunca se usa en Wayland, aunque exista DISPLAY.

Se capturan texto UTF-8 e imágenes PNG/JPEG/WebP anunciados por el propietario del portapapeles; no PRIMARY ni todos los formatos de archivos. Cada transferencia está limitada a 16 MiB. Cambios muy rápidos pueden perder entradas: se descartan respuestas de propietarios anteriores. No hay persistencia del portapapeles del sistema cuando su propietario desaparece. La lista JSON sí persiste.

Seleccionar un elemento solicita al Shell publicar el contenido y pegar en la ventana anterior. Se verifica el foco antes de emitir Ctrl+V; si el destino ya no existe o quedan modificadores pulsados, solo se copia. Terminales que requieren Ctrl+Shift+V y aplicaciones que no aceptan Ctrl+V necesitan pegado manual. No hay garantía de aceptación por la aplicación destino. La selección/paste no tiene confirmación visual de error todavía; consultar registros si falta la extensión o se supera el límite.


## Estado de validación

La VM confirmó la carga ACTIVE de la extensión versión 2. La versión 0.2.2 corrige el cierre de Python con esa extensión activa. El atajo, arrastre, posición, captura en segundo plano y pegado completos siguen pendientes de confirmación en la VM.
