from __future__ import annotations

from pathlib import Path

import json5

from .models import AppConfig


def load_config(path: Path) -> AppConfig:
    data = json5.loads(path.read_text(encoding="utf-8"))
    return AppConfig.model_validate(data)
