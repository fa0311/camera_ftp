from __future__ import annotations

from pathlib import Path
from typing import Callable

from celery import Celery
from celery.result import AsyncResult
from pydantic import AnyUrl


class TaskWorker:
    def __init__(self, broker: AnyUrl):
        self.celery = Celery(
            "photoftp",
            broker=str(broker),
        )

    def add_task(self, path: Path) -> AsyncResult:
        return self.celery.send_task("photoftp.process_file", args=[str(path)])

    def worker(self, argv: list[str], callable: Callable[[Path], None]):
        def process_file(path: str):
            callable(Path(path))

        self.celery.task(name="photoftp.process_file")(process_file)
        self.celery.worker_main(argv=["worker"] + argv)
