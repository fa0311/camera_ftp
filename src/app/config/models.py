from __future__ import annotations

from pathlib import Path
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field


# -----------------------
# pipeline ops
# -----------------------
class ExposureOp(BaseModel):
    type: Literal["exposure"]
    ev: float = 0.0


class ContrastOp(BaseModel):
    type: Literal["contrast"]
    factor: float = 1.0


class SaturationOp(BaseModel):
    type: Literal["saturation"]
    factor: float = 1.0


class SharpnessOp(BaseModel):
    type: Literal["sharpness"]
    amount: float = 0.0
    radius: float = 1.0


PipelineOp = Annotated[
    Union[ExposureOp, ContrastOp, SaturationOp, SharpnessOp],
    Field(discriminator="type"),
]


# -----------------------
# inputs
# -----------------------
class RawDecodeOptions(BaseModel):
    white_balance: Literal["camera", "auto", "custom"] = "camera"
    gamma: Literal["linear", "srgb"] = "linear"
    output_color: str = "srgb"


class RawInput(BaseModel):
    type: Literal["raw"]
    path_globs: List[str]
    raw: Optional[RawDecodeOptions] = None


class ImageInput(BaseModel):
    type: Literal["image"]
    path_globs: List[str]


Input = Annotated[
    Union[RawInput, ImageInput],
    Field(discriminator="type"),
]


# -----------------------
# outputs
# -----------------------
class JpegOutput(BaseModel):
    type: Literal["jpeg"]
    path: str

    quality: int = 95
    subsampling: Literal["4:4:4", "4:2:2", "4:2:0"] = "4:2:0"
    progressive: bool = True


class WebpOutput(BaseModel):
    type: Literal["webp"]
    path: str

    quality: int = 90
    lossless: bool = False


Output = Annotated[
    Union[JpegOutput, WebpOutput],
    Field(discriminator="type"),
]


# -----------------------
# rule / config
# -----------------------
class Rule(BaseModel):
    name: str
    input: List[Input]
    pipeline: List[PipelineOp] = []
    outputs: List[Output]


class AppConfig(BaseModel):
    out_dir: Path = Path("data/output")
    rules: List[Rule]
