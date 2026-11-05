"""Run with dbus-run-session; never uses the user's session bus."""
import base64
import tempfile
from pathlib import Path
from PySide6.QtCore import QTimer, QObject, ClassInfo, Slot
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage
from PySide6.QtWidgets import QApplication
from clipboard import ClipboardWatcher
from history import HistoryStore
from gnome_bridge import APP_ID, PATH, EXTENSION, GnomeBridge
import json
import time

app = QApplication([])
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    watcher = ClipboardWatcher(app.clipboard(), HistoryStore(root / 'history.json', root / 'cache'), root / 'cache', monitor=False)
    commands = []
    bridge = GnomeBridge(watcher, commands.append, {})
    import subprocess
    import sys
    log = root / 'requests.jsonl'
    peer = subprocess.Popen([sys.executable, 'tests/shell_peer.py', str(log)])
    import atexit
    atexit.register(peer.terminate)
    deadline = time.monotonic() + 5
    while not log.exists() and time.monotonic() < deadline:
        time.sleep(.01)
    assert log.exists()
    bridge.configure()
    assert bridge.request('show')
    bridge.paste({'type': 'text', 'content': ' paste '})
    deadline = time.monotonic() + 3
    while len(log.read_text().splitlines()) < 3 and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.01)
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [r['action'] for r in requests] == ['configure', 'show', 'paste'], requests
    assert base64.b64decode(requests[-1]['data']) == b' paste '
    peer.terminate()
    peer.wait(timeout=5)
    interface = QDBusInterface(APP_ID, PATH, APP_ID, QDBusConnection.sessionBus())
    assert interface.isValid()
    reply = interface.call('Capture', 'text/plain', base64.b64encode(b' \n dbus.png \n ').decode())
    assert reply.type() != QDBusMessage.MessageType.ErrorMessage, reply.errorMessage()
    assert watcher.history.items[0]['content'] == ' \n dbus.png \n '
    reply = interface.call('Toggle')
    assert reply.type() != QDBusMessage.MessageType.ErrorMessage, reply.errorMessage()
    assert commands == ['toggle']
    print('D-Bus: export, Capture and Toggle OK')
