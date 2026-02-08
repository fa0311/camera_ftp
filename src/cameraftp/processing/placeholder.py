from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Dict


class Format:
    def __init__(self, format: Callable[[str], str]):
        self.format = format

    def __format__(self, spec: str) -> str:
        return self.format(spec)


def _file_sha256_hex(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def placeholder_format(src_path: Path, placeholder: str) -> Path:
    file_hash = _file_sha256_hex(src_path)
    ctx_base: Dict[str, Any] = {
        "stem": src_path.stem,
        "ext": src_path.suffix.lstrip(".").lower(),
        "file": src_path.name,
        "hash": file_hash,
        "hash8": file_hash[:8],
        "now": Format(lambda s: datetime.now().strftime(s)),
    }
    return Path(placeholder.format(**ctx_base))
