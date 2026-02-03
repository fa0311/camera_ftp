from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict

import imageio.v3 as iio
import numpy as np

from app.config.models import Output


@dataclass(frozen=True)
class _NowToken:
    dt: datetime

    def __format__(self, spec: str) -> str:
        return self.dt.strftime(spec)


def _file_sha256_hex(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_outputs(
    img_f32: np.ndarray, outputs: list[Output], out_dir: Path, src_path: Path
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    now = _NowToken(datetime.now())
    file_hash = _file_sha256_hex(src_path)

    ctx_base: Dict[str, Any] = {
        "stem": src_path.stem,
        "ext": src_path.suffix.lstrip(".").lower(),
        "file": src_path.name,
        "hash": file_hash,
        "hash8": file_hash[:8],
        "now": now,
    }

    img_u8 = (np.clip(img_f32, 0.0, 1.0) * 255.0).astype(np.uint8)

    for o in outputs:
        rel = Path(o.path.format(**ctx_base))

        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)

        if o.type == "jpeg":
            subsampling_map = {
                "4:4:4": 0,
                "4:2:2": 1,
                "4:2:0": 2,
            }
            iio.imwrite(
                path,
                img_u8,
                quality=int(o.quality),
                progressive=bool(o.progressive),
                subsampling=subsampling_map[o.subsampling],
            )
        elif o.type == "webp":
            iio.imwrite(
                path,
                img_u8,
                quality=int(o.quality),
                lossless=bool(o.lossless),
            )
