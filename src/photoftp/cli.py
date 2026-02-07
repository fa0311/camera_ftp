from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from photoftp.config.env import Env
from photoftp.config.loader import load_config
from photoftp.ftp.server import FTPWorker, parse_passive_ports
from photoftp.processing.decode_image import decode_image_to_float32
from photoftp.processing.decode_raw import decode_raw_to_float32
from photoftp.processing.encode import write_outputs
from photoftp.processing.matcher import match_all
from photoftp.processing.pipeline import apply_pipeline
from photoftp.queue.tasks import TaskWorker

app = typer.Typer()


@app.command()
def validate_config(
    config: Path = typer.Argument(..., exists=True),
):
    cfg = load_config(config)
    print("[green]OK[/green]")
    print(f"rules: {len(cfg.rules)}")


@app.command()
def enqueue(
    target: Path = typer.Argument(...),
):
    env = Env()
    settings = load_config(env.config_path)
    task_worker = TaskWorker(settings.broker)
    r = task_worker.add_task(target)
    print(f"[green]Enqueued[/green] task id: {r.id}")


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def worker(ctx: typer.Context):
    """Run a Celery worker (pass-through args supported)."""

    env = Env()
    settings = load_config(env.config_path)
    task_worker = TaskWorker(settings.broker)

    def process_file(src: Path):
        matches = match_all(settings.rules, src)
        print(f"Processing {src}: found {len(matches)} matches")
        input = settings.mount_path.resolve(strict=True).joinpath(src)
        for m in matches:
            if m.input.type == "raw":
                img = decode_raw_to_float32(input, m.input.options)
            elif m.input.type == "image":
                img = decode_image_to_float32(input, m.input.options)
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
    settings = load_config(env.config_path)
    task_worker = TaskWorker(settings.broker)
    mount_abs = settings.mount_path.resolve(strict=True)

    def on_file_received(path: Path):
        relative = path.resolve(strict=True).relative_to(mount_abs)
        print(f"Enqueued task for {relative}")
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
    print(f"Starting FTP server on {host}:{port}...")
    worker.worker(host, port)
