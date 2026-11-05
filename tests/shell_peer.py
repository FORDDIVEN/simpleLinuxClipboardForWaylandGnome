"""D-Bus Shell stand-in for integration tests, with actual Qt event dispatch."""
import json
import sys
from pathlib import Path
from PySide6.QtCore import QObject, ClassInfo, Slot
from PySide6.QtDBus import QDBusConnection
from PySide6.QtWidgets import QApplication
from gnome_bridge import EXTENSION, PATH

app = QApplication([])
log = Path(sys.argv[1])
@ClassInfo(**{'D-Bus Interface': EXTENSION})
class Peer(QObject):
    @Slot(str)
    def Request(self, payload):
        with log.open('a') as stream:
            stream.write(json.dumps(json.loads(payload)) + '\n')
peer = Peer()
bus = QDBusConnection.sessionBus()
assert bus.registerService(EXTENSION)
assert bus.registerObject(PATH, peer, QDBusConnection.RegisterOption.ExportAllSlots)
log.touch()
app.exec()
