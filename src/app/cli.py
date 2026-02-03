from __future__ import annotations

from pathlib import Path

import typer
from rich import print

from app.config.loader import load_config
from app.ftp.server import run_ftp_server
from app.processing.matcher import match_all
from app.queue.celery_app import celery_app

app = typer.Typer(add_completion=False)


@app.command()
def validate_config(config: Path = typer.Argument(..., exists=True)):
    cfg = load_config(config)
    print("[green]OK[/green]")
    print(f"rules: {len(cfg.rules)}")


@app.command()
def enqueue(
    target: Path = typer.Argument(...),
    config: Path = typer.Option(Path("configs/config.sample.jsonc"), "--config", "-c"),
):
    cfg = load_config(config)
    matches = match_all(cfg, target)
    if not matches:
        print("[yellow]No match[/yellow]")
        raise typer.Exit(code=1)

    for m in matches:
        r = celery_app.send_task(
            "photoftp.process_file",
            args=[str(config), str(target), m.rule_index, m.input_index],
        )
        print(f"[green]Enqueued[/green] rule={m.rule.name} task_id={r.id}")


@app.command()
def ftp_serve(
    config: Path = typer.Option(Path("configs/config.sample.jsonc"), "--config", "-c"),
    incoming: Path = typer.Option(Path("incoming"), "--incoming", "-i"),
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(2121, "--port"),
    user: str = typer.Option("user", "--user"),
    password: str = typer.Option("pass", "--password"),
):
    """
    FTPサーバを起動して、アップロード完了時にenqueueします。
    """
    run_ftp_server(
        config_path=config,
        incoming_dir=incoming,
        host=host,
        port=port,
        user=user,
        password=password,
    )


if __name__ == "__main__":
    app()
