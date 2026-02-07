from __future__ import annotations

import cv2
import numpy as np

from photoftp.config.models import PipelineOp


def apply_pipeline(img: np.ndarray, ops: list[PipelineOp]) -> np.ndarray:
    out = img
    for op in ops:
        if op.type == "exposure":
            out = out * (2.0 ** float(op.ev))

        elif op.type == "contrast":
            c = float(op.factor)
            out = (out - 0.5) * c + 0.5

        elif op.type == "saturation":
            s = float(op.factor)
            luma = (0.2126 * out[..., 0] + 0.7152 * out[..., 1] + 0.0722 * out[..., 2])[
                ..., None
            ]
            out = luma + (out - luma) * s

        elif op.type == "sharpness":
            amount = float(op.amount)
            radius = float(op.radius)

            if amount != 0.0:
                sigma = radius
                blurred = cv2.GaussianBlur(out, (0, 0), sigmaX=sigma, sigmaY=sigma)
                out = out + amount * (out - blurred)

    return np.clip(out, 0.0, 1.0)
