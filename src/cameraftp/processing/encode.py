from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import cv2
import imageio.v3 as iio
import numpy as np

from cameraftp.config.models import Output
from cameraftp.processing.placeholder import placeholder_format

logger = logging.getLogger(__name__)


def write_outputs(
    img_f32: np.ndarray,
    outputs: list[Output],
    out_dir: Path,
    src_path: Path,
) -> None:
    def convert(kind: Literal["u8", "u16", "f32"]) -> np.ndarray:
        if kind == "u8":
            return (np.clip(img_f32, 0.0, 1.0) * 255.0).astype(np.uint8)
        elif kind == "u16":
            return (np.clip(img_f32, 0.0, 1.0) * 65535.0).astype(np.uint16)
        elif kind == "f32":
            return img_f32.astype(np.float32, copy=False)
        else:
            raise ValueError(f"Unknown convert kind: {kind}")

    def to_bgr(kind: Literal["u8", "u16", "f32"]) -> np.ndarray:
        return cv2.cvtColor(convert(kind), cv2.COLOR_RGB2BGR)

    for o in outputs:
        rel = placeholder_format(src_path, o.path)
        path = out_dir.joinpath(rel)
        path.parent.mkdir(parents=True, exist_ok=True)

        if o.type == "jpeg":
            subsampling_map = {
                "4:4:4": cv2.IMWRITE_JPEG_SAMPLING_FACTOR_444,
                "4:2:2": cv2.IMWRITE_JPEG_SAMPLING_FACTOR_422,
                "4:2:0": cv2.IMWRITE_JPEG_SAMPLING_FACTOR_420,
                "4:1:1": cv2.IMWRITE_JPEG_SAMPLING_FACTOR_411,
                "4:4:0": cv2.IMWRITE_JPEG_SAMPLING_FACTOR_440,
            }
            cv2.imwrite(
                str(path),
                to_bgr("u8"),
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    o.quality,
                    cv2.IMWRITE_JPEG_PROGRESSIVE,
                    1 if o.progressive else 0,
                    cv2.IMWRITE_JPEG_SAMPLING_FACTOR,
                    subsampling_map[o.subsampling],
                ],
            )
        elif o.type == "webp":
            params = [cv2.IMWRITE_WEBP_QUALITY, o.quality]
            cv2.imwrite(str(path), to_bgr("u8"), params)
        elif o.type == "imageio-webp":
            iio.imwrite(
                path,
                convert("u8"),
                quality=o.quality,
                lossless=o.lossless,
            )
        elif o.type == "png":
            if o.dtype == "uint8":
                bgr = to_bgr("u8")
            elif o.dtype == "uint16":
                bgr = to_bgr("u16")
            else:
                bgr = to_bgr("f32")
            cv2.imwrite(
                str(path),
                bgr,
                [cv2.IMWRITE_PNG_COMPRESSION, o.compression],
            )
        elif o.type == "tiff":
            if o.dtype == "uint8":
                bgr = to_bgr("u8")
            elif o.dtype == "uint16":
                bgr = to_bgr("u16")
            else:
                bgr = to_bgr("f32")
            cv2.imwrite(
                str(path),
                bgr,
                [cv2.IMWRITE_TIFF_COMPRESSION, o.compression],
            )
        logger.info("Wrote output: %s", path)
