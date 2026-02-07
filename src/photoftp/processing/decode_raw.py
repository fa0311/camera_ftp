from __future__ import annotations

from pathlib import Path

import numpy as np
import rawpy

from photoftp.config.models import RawDecodeOptions


def decode_raw_to_float32(path: Path, opt: RawDecodeOptions) -> np.ndarray:
    print(f"Decoding RAW file {str(path)} with options: {opt}")

    with rawpy.imread(str(path)) as raw:
        if opt and opt.white_balance == "auto":
            rgb = raw.postprocess(use_auto_wb=True, use_camera_wb=False, output_bps=16)
        else:
            rgb = raw.postprocess(use_auto_wb=False, use_camera_wb=True, output_bps=16)

    img = rgb.astype(np.float32) / 65535.0
    return img
