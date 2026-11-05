# WinV Clipboard Wayland

Historial de portapapeles para **GNOME 50 sobre Wayland**, con aplicación
Python/PySide6 y una extensión de GNOME Shell. Basado en
[simpleLinuxClipboard para X11](https://github.com/FORDDIVEN/simpleLinuxClipboard),
y desarrollado como proyecto independiente. Consulta [origen y atribución](ORIGIN.md).

Guarda textos e imágenes, permite buscar y fijar elementos y mantiene una
instancia residente. La extensión proporciona el atajo global, la captura en
segundo plano, el control de posición y el pegado al seleccionar.

**Estado: experimental, versión 0.2.2.** La extensión versión 2 cargó ACTIVE en
la VM de prueba. La validación completa de atajo, arrastre, posición, captura
y pegado en GNOME/Wayland sigue pendiente. No se anuncia soporte para otros
escritorios Wayland.

## Instalación en Ubuntu / GNOME 50

Descarga el paquete amd64 desde las Releases del nuevo repositorio, cuando
estén publicadas. Desde la carpeta de descarga:

```bash
sudo apt install ./winvclipboard-wayland_0.2.2~gnome50.1_amd64.deb
```

Cierra sesión y vuelve a entrar. Después, sin sudo:

```bash
gnome-extensions enable winvclipboard-wayland@local
gnome-extensions info winvclipboard-wayland@local
winvclipboard-wayland --show
```

La extensión debe indicar `ACTIVE`. El paquete incluye Python/PySide6,
la extensión y autoinicio en GNOME. No activa la extensión ni cambia atajos
del sistema automáticamente. En actualizaciones con la extensión ya activa
no hace falta repetir su habilitación.

El atajo predeterminado es **Super+V**. Si GNOME lo usa para notificaciones,
cambia esa asignación o la combinación de la app. Arrastra desde el título
para mover la ventana.

[Instalación, actualización y desinstalación](packaging/debian/VM-INSTALL.md).

## Uso

```bash
winvclipboard-wayland --show
winvclipboard-wayland --hide
winvclipboard-wayland --toggle
winvclipboard-wayland --quit
```

Los datos están separados de X11: `~/.local/share/winvclipboard-wayland/`
y `~/.cache/winvclipboard-wayland/`. El historial se guarda en texto plano.

## Desarrollo y documentación

- [Ejecutar desde fuentes, probar y construir el .deb](docs/DEVELOPMENT.md).
- [Arquitectura, decisiones y limitaciones de GNOME](docs/INTEGRATION.md).
- [Publicar como repositorio independiente](docs/PUBLISHING.md).
- [Cambios por versión](CHANGELOG.md).
- [Origen y estado de la licencia](ORIGIN.md).

```text
*.py                 Aplicación Python y backend X11 heredado.
assets/              Icono de la aplicación.
gnome-extension/     Extensión GNOME y esquema GSettings.
packaging/debian/    Lanzadores e instrucciones del paquete.
scripts/             Construcción del .deb.
tests/               Regresiones y pruebas D-Bus/IPC aisladas.
docs/                Documentación de desarrollo e integración.
dist/                Paquetes generados, excluidos de Git.
```
