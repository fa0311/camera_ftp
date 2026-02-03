from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import rawpy

from app.config.models import RawDecodeOptions


def decode_raw_to_float32(path: Path, opt: Optional[RawDecodeOptions]) -> np.ndarray:
    with rawpy.imread(str(path)) as raw:
        # MVP: WBだけ切替（他はYAGNIで固定）
        if opt and opt.white_balance == "auto":
            rgb = raw.postprocess(use_auto_wb=True, use_camera_wb=False, output_bps=16)
        else:
            # camera/custom は一旦 camera 扱い（customは将来拡張）
            rgb = raw.postprocess(use_auto_wb=False, use_camera_wb=True, output_bps=16)

    # uint16 -> float32 0..1
    img = rgb.astype(np.float32) / 65535.0
    return img
