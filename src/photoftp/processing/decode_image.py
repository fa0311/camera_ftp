from __future__ import annotations

from pathlib import Path

import numpy as np
import pillow_heif
from PIL import Image

from photoftp.config.models import ImageDecodeOptions

pillow_heif.register_heif_opener()


def decode_image_to_float32(path: Path, opt: ImageDecodeOptions) -> np.ndarray:
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img).astype(np.float32) / 255.0
    return arr
