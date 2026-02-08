from __future__ import annotations

from pathlib import Path

import numpy as np
import rawpy


def decode_raw_to_float32(path: Path, white_balance: str) -> np.ndarray:
    with rawpy.imread(str(path)) as raw:
        if white_balance == "auto":
            rgb = raw.postprocess(use_auto_wb=True, use_camera_wb=False, output_bps=16)
        else:
            rgb = raw.postprocess(use_auto_wb=False, use_camera_wb=True, output_bps=16)

    img = rgb.astype(np.float32) / 65535.0
    return img
