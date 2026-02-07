from __future__ import annotations

from pathlib import Path

import imageio.v3 as iio
import numpy as np

from photoftp.config.models import Output
from photoftp.processing.placeholder import placeholder_format


def write_outputs(
    img_f32: np.ndarray,
    outputs: list[Output],
    out_dir: Path,
    src_path: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    img_u8 = (np.clip(img_f32, 0.0, 1.0) * 255.0).astype(np.uint8)  # type: ignore

    for o in outputs:
        rel = placeholder_format(src_path, o.path)
        path = out_dir.joinpath(rel)
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
        print(f"Wrote output: {path}")
