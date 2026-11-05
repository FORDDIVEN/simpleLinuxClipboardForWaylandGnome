"""Isolated resident-process/IPC smoke test; run in a private D-Bus session."""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    os.environ.update(XDG_RUNTIME_DIR=str(root), QT_QPA_PLATFORM='offscreen',
                      XDG_SESSION_TYPE='wayland',
                      WINVCLIPBOARD_WAYLAND_DATA_DIR=str(root / 'data'),
                      WINVCLIPBOARD_WAYLAND_CACHE_DIR=str(root / 'cache'))
    from ipc import send_command
    command = [os.environ['WINV_TEST_BINARY']] if os.environ.get('WINV_TEST_BINARY') else [sys.executable, 'main.py']
    peer_log = root / 'shell.jsonl'
    peer = subprocess.Popen([sys.executable, 'tests/shell_peer.py', str(peer_log)])
    deadline = time.monotonic() + 5
    while not peer_log.exists() and time.monotonic() < deadline:
        time.sleep(.01)
    assert peer_log.exists(), 'Shell stand-in did not start'
    process = subprocess.Popen(command + ['--background'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 5
        while not send_command('noop'):
            if process.poll() is not None:
                raise AssertionError(process.communicate())
            if time.monotonic() > deadline:
                raise AssertionError('IPC unavailable')
            time.sleep(.05)
        for command in ['show', 'hide', 'toggle', 'hide']:
            assert send_command(command), command
        deadline = time.monotonic() + 3
        while '"action": "show"' not in peer_log.read_text() and time.monotonic() < deadline:
            time.sleep(.01)
        requests = peer_log.read_text()
        assert '"action": "configure"' in requests, requests
        assert '"action": "show"' in requests, requests
        assert process.poll() is None
        assert send_command('quit')
        out, err = process.communicate(timeout=5)
        assert process.returncode == 0, (out, err)
        assert (root / 'data' / 'history.json').exists()
        print('Resident Wayland process with Shell service: configure/show + IPC OK')
    finally:
        peer.terminate()
        peer.wait(timeout=5)
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
