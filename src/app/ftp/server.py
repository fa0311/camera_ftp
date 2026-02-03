from __future__ import annotations

from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from app.config.loader import load_config
from app.processing.matcher import match_all
from app.queue.celery_app import celery_app


def run_ftp_server(
    *,
    config_path: Path,
    incoming_dir: Path,
    host: str,
    port: int,
    user: str,
    password: str,
) -> None:
    cfg = load_config(config_path)
    incoming_dir.mkdir(parents=True, exist_ok=True)

    class _Handler(FTPHandler):
        def on_file_received(self, file: str) -> None:
            p = Path(file)
            matches = match_all(cfg, p)
            for m in matches:
                celery_app.send_task(
                    "photoftp.process_file",
                    args=[str(config_path), str(p), m.rule_index, m.input_index],
                )

    authorizer = DummyAuthorizer()
    authorizer.add_user(user, password, str(incoming_dir), perm="elradfmwMT")

    _Handler.authorizer = authorizer

    server = FTPServer((host, port), _Handler)
    server.serve_forever()
