"""Private session-bus integration with the GNOME Shell companion."""
import base64
import json
import logging

from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QObject, ClassInfo, Slot
from PySide6.QtDBus import QDBusConnection, QDBusInterface
from PySide6.QtGui import QImage
from config import APP_ID

PATH = '/io/github/winvclipboard/Wayland'
EXTENSION = APP_ID + '.Shell'
MAX_BYTES = 16 * 1024 * 1024


@ClassInfo(**{'D-Bus Interface': APP_ID})
class GnomeBridge(QObject):

    def __init__(self, watcher, command, settings):
        super().__init__()
        self.watcher = watcher
        self.command = command
        self.settings = settings
        self.bus = QDBusConnection.sessionBus()
        if not self.bus.registerService(APP_ID):
            raise RuntimeError('No se pudo registrar el servicio D-Bus de Wayland')
        if not self.bus.registerObject(PATH, self, QDBusConnection.RegisterOption.ExportAllSlots):
            raise RuntimeError('No se pudo exportar la integración GNOME')

    @Slot()
    def Toggle(self):
        self.command('toggle')

    @Slot(str, str)
    def Capture(self, mime, encoded):
        if len(encoded) > MAX_BYTES * 4 // 3 + 4:
            return
        try:
            data = base64.b64decode(encoded, validate=True)
            if mime == 'text/plain':
                self.watcher._add_text(data.decode('utf-8'))
            elif mime.startswith('image/'):
                self.watcher._add_image(QImage.fromData(data))
        except (ValueError, UnicodeError):
            logging.exception('Contenido de portapapeles inválido')

    @Slot(int, int)
    def Position(self, x, y):
        from settings import save_settings
        self.settings['window_position'] = [x, y]
        save_settings(self.settings)

    @Slot()
    def Ready(self):
        self.configure()

    def request(self, action, **values):
        interface = QDBusInterface(EXTENSION, PATH, EXTENSION, self.bus)
        if not interface.isValid():
            logging.warning('Extensión GNOME no disponible: %s', action)
            return False
        interface.asyncCallWithArgumentList('Request', [json.dumps({'action': action, **values})])
        return True

    def configure(self):
        self.request('configure', enabled=self.settings.get('global_hotkey_enabled', True),
                     shortcut=self.settings.get('global_hotkey', 'Meta+V'),
                     position=self.settings.get('window_position'))

    def paste(self, item):
        if item['type'] == 'text':
            mime, data = 'text/plain', item['content'].encode('utf-8')
        else:
            image = QImage(item['path'])
            data = QByteArray()
            buffer = QBuffer(data)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            if not image.save(buffer, 'PNG'):
                return
            data, mime = bytes(data), 'image/png'
        if len(data) > MAX_BYTES:
            logging.warning('Elemento demasiado grande para el puente GNOME (16 MiB)')
            return
        if not self.request('paste', mime=mime, data=base64.b64encode(data).decode('ascii')):
            from PySide6.QtGui import QGuiApplication
            clipboard = QGuiApplication.clipboard()
            if mime == 'text/plain':
                clipboard.setText(item['content'])
            else:
                clipboard.setImage(QImage(item['path']))
