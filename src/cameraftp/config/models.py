from __future__ import annotations

from pathlib import Path

from pydantic import AnyUrl, BaseModel, ConfigDict


class ConfigBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Output(ConfigBase):
    path: str
    args: list[str] = []


class Rule(ConfigBase):
    name: str | None = None
    input_globs: list[str]
    input_args: list[str] = []
    outputs: list[Output]


class AppConfig(ConfigBase):
    mount_path: Path = Path("images")
    broker: AnyUrl
    magick: str = "convert"
    exiftool: str = "exiftool"
    rules: list[Rule]
