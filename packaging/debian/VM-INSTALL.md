# Prueba en Ubuntu GNOME 50 / Wayland (amd64)

Instala el paquete desde la carpeta donde lo copiaste:

```bash
sudo apt install ./winvclipboard-wayland_0.2.2~gnome50.1_amd64.deb
```

Incluye Python/PySide6 privados; no necesitas pip ni el código fuente.
Instala la extensión para todos los usuarios y añade autoinicio en GNOME.
No activa la extensión, no modifica atajos del sistema ni toca el historial X11.

Cierra sesión y vuelve a entrar (reiniciar solo la app no basta para descubrir
una extensión nueva). Como usuario normal, sin sudo:

```bash
gnome-extensions enable winvclipboard-wayland@local
winvclipboard-wayland --show
```

El proceso arranca en segundo plano al iniciar sesión. Arrastra el título para
moverlo. Comprueba Super+V; GNOME puede tener esa combinación asignada a las
notificaciones. Cambia ese atajo en Configuración de GNOME o el de esta app.
No hay que configurar un comando personalizado para cada pulsación.

Si habías instalado una copia manual de la misma extensión en
~/.local/share/gnome-shell/extensions/winvclipboard-wayland@local, esa copia
puede tener prioridad sobre la del paquete: retírala o renómbrala antes de
cerrar sesión para probar exactamente la versión del .deb.

Diagnóstico:

```bash
gnome-extensions info winvclipboard-wayland@local
journalctl --user -b -o cat | rg -i 'winv|clipboard|extension'
winvclipboard-wayland --quit
winvclipboard-wayland
```

Si no tienes rg, usa grep -Ei en su lugar. Arrancar desde terminal permite ver
los mensajes Python. Verifica texto e imágenes copiadas con el panel oculto,
pegado en un editor, ubicación tras reiniciar y convivencia con la app X11.
Los terminales pueden necesitar Ctrl+Shift+V manualmente.

Para detener y desinstalar:

```bash
winvclipboard-wayland --quit
gnome-extensions disable winvclipboard-wayland@local
sudo apt remove winvclipboard-wayland
```

Los datos personales en ~/.local/share/winvclipboard-wayland y
~/.cache/winvclipboard-wayland se conservan. Puedes desactivar el autoinicio
desde Aplicaciones al inicio sin desinstalar el paquete.

Paquete experimental: se comprueba el arranque aislado y su contenido, pero
no se ha probado la extensión dentro de GNOME 50 real en el equipo de compilación.

Al actualizar desde 0.2.0, detén la app con --quit antes de instalar.
Cierra sesión y vuelve a entrar después de actualizar: Shell puede conservar
el módulo JavaScript anterior aunque desactives y reactives la extensión.
