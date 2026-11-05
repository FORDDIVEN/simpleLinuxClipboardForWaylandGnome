from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4


def new_id() -> str:
    return uuid4().hex


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def remove_file(path: str | Path) -> None:
    target = Path(path)
    try:
        if target.is_file():
            target.unlink()
    except OSError:
        pass


def file_sha256(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload) -> None:
    import json
    import os
    import tempfile
    ensure_dir(path.parent)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
