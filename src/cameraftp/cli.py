from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer

from cameraftp.config.env import Env
from cameraftp.config.loader import load_config
from cameraftp.ftp.server import FTPWorker, parse_passive_ports
from cameraftp.logging_config import setup_logging
from cameraftp.processing.decode_image import decode_image_to_float32
from cameraftp.processing.decode_raw import decode_raw_to_float32
from cameraftp.processing.encode import write_outputs
from cameraftp.processing.matcher import match_all
from cameraftp.processing.pipeline import apply_pipeline
from cameraftp.queue.tasks import TaskWorker

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command()
def validate_config(
    config: Path = typer.Argument(..., exists=True),
):
    env = Env()
    setup_logging(env.log_level)
    cfg = load_config(config)
    logger.info("OK")
    logger.info("rules: %d", len(cfg.rules))


@app.command()
def enqueue(
    target: Path = typer.Argument(...),
):
    env = Env()
    setup_logging(env.log_level)
    settings = load_config(env.config_path)
    task_worker = TaskWorker(settings.broker)
    r = task_worker.add_task(target)
    logger.info("Enqueued task id: %s", r.id)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def worker(ctx: typer.Context):
    """Run a Celery worker (pass-through args supported)."""

    env = Env()
    setup_logging(env.log_level)
    settings = load_config(env.config_path)
    task_worker = TaskWorker(settings.broker)

    def process_file(src: Path):
        matches = match_all(settings.rules, src)
        logger.info("Processing %s: found %d matches", src, len(matches))
        input = settings.mount_path.resolve(strict=True).joinpath(src)
        for m in matches:
            if m.input.type == "raw":
                img = decode_raw_to_float32(input, m.input.white_balance)
            elif m.input.type == "image":
                img = decode_image_to_float32(input)
            else:
                raise ValueError(f"Unknown input type: {m.input.type}")

            img = apply_pipeline(img, m.rule.pipeline)
            write_outputs(
                img,
                m.rule.outputs,
                settings.mount_path,
                src_path=input,
            )

    task_worker.worker(ctx.args, process_file)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(21, "--port"),
    user: str = typer.Option("user", "--user"),
    password: str = typer.Option("pass", "--password"),
    passive_ports: str = typer.Option("30000-30010", "--passive-ports"),
    masquerade_address: Optional[str] = typer.Option(None, "--masquerade-address"),
):

    env = Env()
    setup_logging(env.log_level)
    settings = load_config(env.config_path)
    task_worker = TaskWorker(settings.broker)
    mount_abs = settings.mount_path.resolve(strict=True)

    def on_file_received(path: Path):
        relative = path.resolve(strict=True).relative_to(mount_abs)
        logger.info("Enqueued task for %s", relative)
        task_worker.add_task(relative)

    worker = FTPWorker(
        on_file_received=on_file_received,
        passive_ports=parse_passive_ports(passive_ports),
        masquerade_address=masquerade_address,
    )
    worker.add_user(
        username=user,
        password=password,
        homedir=settings.mount_path,
        perm="elradfmwMT",
    )
    logger.info("Starting FTP server on %s:%s...", host, port)
    worker.worker(host, port)
