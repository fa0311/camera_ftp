from __future__ import annotations

from pathlib import Path
from typing import Annotated, List, Literal, Union

from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class ConfigBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


# -----------------------
# pipeline ops
# -----------------------
class ExposureOp(ConfigBase):
    type: Literal["exposure"]
    ev: float = 0.0


class ContrastOp(ConfigBase):
    type: Literal["contrast"]
    factor: float = 1.0


class SaturationOp(ConfigBase):
    type: Literal["saturation"]
    factor: float = 1.0


class SharpnessOp(ConfigBase):
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


class RawInput(ConfigBase):
    type: Literal["raw"]
    path_globs: List[str]
    options: RawDecodeOptions


class RawDecodeOptions(ConfigBase):
    white_balance: Literal["camera", "auto"] = "camera"


class ImageDecodeOptions(ConfigBase):
    pass


class ImageInput(ConfigBase):
    type: Literal["image"]
    path_globs: List[str]
    options: ImageDecodeOptions


Input = Annotated[
    Union[RawInput, ImageInput],
    Field(discriminator="type"),
]


# -----------------------
# outputs
# -----------------------
class JpegOutput(ConfigBase):
    type: Literal["jpeg"]
    path: str

    quality: int = 95
    subsampling: Literal["4:4:4", "4:2:2", "4:2:0"] = "4:2:0"
    progressive: bool = True


class WebpOutput(ConfigBase):
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
class Rule(ConfigBase):
    name: str
    input: List[Input]
    pipeline: List[PipelineOp] = []
    outputs: List[Output]


class AppConfig(ConfigBase):
    mount_path: Path = Path("images")
    broker: AnyUrl
    rules: List[Rule]
