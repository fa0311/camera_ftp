from __future__ import annotations

import logging

from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> None:
    handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
    )
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[handler],
    )
