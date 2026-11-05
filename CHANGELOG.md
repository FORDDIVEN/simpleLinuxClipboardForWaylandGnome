# Cambios

## 0.2.2 — experimental

- Corrige las llamadas salientes de PySide6 usando `asyncCallWithArgumentList`.
- Usa GLib del sistema en el .deb para evitar mezclarla con módulos GVfs nuevos.
- Añade pruebas D-Bus con un servicio Shell simulado activo.

## 0.2.1 — experimental

- Corrige la API del teclado virtual en GNOME 50 y lo crea al pegar.
- Refuerza el arrastre del título mediante un filtro de eventos Qt.

## 0.2.0 — primera adaptación

- Separa datos, configuración, IPC e identidad de la aplicación X11.
- Añade extensión GNOME y puente D-Bus.
- Corrige preservación del texto, JSON null, imágenes duplicadas y guardado atómico.
- Empaqueta aplicación y extensión en un .deb.
