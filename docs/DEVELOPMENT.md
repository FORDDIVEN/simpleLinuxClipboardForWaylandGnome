# Desarrollo

Desde la raíz del repositorio, con Python 3.12+:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python main.py
```

Para ejecutar sin empaquetar basta `requirements.txt`. Para compilar se añade
PyInstaller con `requirements-dev.txt`. Se ha probado localmente con PySide6
6.11.1 / PyInstaller 6.21.0 para el paquete 0.2.2. Las pruebas de fuentes
también pasan con PySide6 6.12.0 en `.venv`; el rango declarado no implica
validar cada versión.

## Instalar la extensión desde fuentes

Esto modifica la sesión del usuario; no lo hacen las pruebas:

```bash
mkdir -p "$HOME/.local/share/gnome-shell/extensions/winvclipboard-wayland@local"
cp -r gnome-extension/. "$HOME/.local/share/gnome-shell/extensions/winvclipboard-wayland@local/"
glib-compile-schemas "$HOME/.local/share/gnome-shell/extensions/winvclipboard-wayland@local/schemas"
```

Cierra sesión, vuelve a entrar y ejecuta:

```bash
gnome-extensions enable winvclipboard-wayland@local
.venv/bin/python main.py --background
```

Una copia local de la extensión puede tener prioridad sobre la del .deb.
Evita mantener ambas al probar paquetes. Al actualizar JavaScript, vuelve a
iniciar sesión para que Shell no conserve el módulo anterior.

## Pruebas

Requieren Node.js, `dbus-run-session`, `glib-compile-schemas` y las bibliotecas
Qt del sistema (en Ubuntu: `libegl1`, `libopengl0`, `libxcb-cursor0`).

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen PYTHONPATH=. dbus-run-session -- .venv/bin/python tests/check_dbus.py
QT_QPA_PLATFORM=offscreen PYTHONPATH=. dbus-run-session -- .venv/bin/python tests/check_instance.py
node tests/check_extension.mjs
node --input-type=module --check < gnome-extension/extension.js
glib-compile-schemas --strict --dry-run gnome-extension/schemas
```

Usan directorios temporales y un bus privado. La prueba JS simula objetos
GNOME; no ejecuta GJS ni valida el compositor real.

## Construir el paquete

En una máquina Ubuntu compatible, instala `dpkg-dev` y `libglib2.0-bin`.

```bash
scripts/build-wayland-deb.sh
```

Usa `.venv/bin/python`, con fallback al antiguo `venv/bin/python`. Puedes
seleccionar el intérprete con `PYTHON=/ruta/python` y la versión con `VERSION`.
El resultado queda en `dist/` junto a su SHA-256. No instala ni activa nada.
El runtime usa GLib del sistema para convivir con los módulos GVfs locales.
El paquete requiere GNOME 50 y glibc >= 2.39. La arquitectura es la del equipo
que compila; el paquete disponible se construyó para amd64.

Los archivos históricos de compilación de la copia local se conservaron en
`.local-archive/`, excluido de Git. No forman parte del proyecto publicado.
