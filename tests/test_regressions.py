import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QMimeData
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from clipboard import ClipboardWatcher
from history import HistoryStore
from utils import atomic_json

app = QApplication.instance() or QApplication([])

class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = HistoryStore(self.root / 'history.json', self.root / 'cache')

    def test_text_roundtrip(self):
        for value in [' \n hello \n ', 'la frase termina en foto.png', ' \n ']:
            self.store.add_text(value)
        loaded = HistoryStore(self.store.history_file, self.store.cache_dir)
        self.assertEqual([i['content'] for i in loaded.items], [' \n ', 'la frase termina en foto.png', ' \n hello \n '])

    def test_malformed_shapes(self):
        for data in [None, {'items': None}, 42, {'items': 'bad'}, [None, 4]]:
            self.store.history_file.write_text(json.dumps(data))
            self.store.load()
            self.assertEqual(self.store.items, [])

    def test_same_image_path_survives(self):
        path = self.store.cache_dir / 'image.png'
        image = QImage(3, 3, QImage.Format.Format_RGB32)
        image.fill(0xff0000)
        image.save(str(path))
        self.store.add_image(path, 'hash')
        self.store.add_image(path, 'hash')
        self.assertTrue(path.exists())
        self.assertEqual(len(self.store.items), 1)

    def test_failed_atomic_replace_preserves_history(self):
        self.store.add_text('saved')
        original = self.store.history_file.read_bytes()
        with patch('os.replace', side_effect=OSError('failure')):
            with self.assertRaises(OSError):
                atomic_json(self.store.history_file, {'items': []})
        self.assertEqual(self.store.history_file.read_bytes(), original)
        self.assertEqual(list(self.root.glob('.history.json.*')), [])

    def test_qt_capture_and_selection(self):
        watcher = ClipboardWatcher(app.clipboard(), self.store, self.store.cache_dir)
        self.addCleanup(lambda: app.clipboard().dataChanged.disconnect(watcher.handle_change))
        app.clipboard().setText(' \n frase.png \n ')
        self.assertEqual(self.store.items[0]['content'], ' \n frase.png \n ')
        image = QImage(4, 4, QImage.Format.Format_RGB32)
        image.fill(0x00ff00)
        app.clipboard().setImage(image)
        self.assertEqual(self.store.items[0]['type'], 'image')
        from ui import ClipboardWindow
        calls = []
        class Integration:
            def paste(self, item): calls.append(item)
        window = ClipboardWindow(self.store, app.clipboard(), integration=Integration())
        item = self.store.items[0]
        window.copy_item(item)
        self.assertEqual(calls, [item])
        window.close()

    def test_title_press_requests_system_move(self):
        from types import SimpleNamespace
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from ui import ClipboardWindow
        window = ClipboardWindow(self.store, app.clipboard())
        self.addCleanup(window.close)
        with patch.object(window, 'windowHandle', return_value=SimpleNamespace(startSystemMove=lambda: True)) as handle:
            QTest.mousePress(window._drag_title, Qt.MouseButton.LeftButton)
            handle.assert_called_once()
            self.assertTrue(window._suppress_auto_hide)

if __name__ == '__main__':
    unittest.main()
