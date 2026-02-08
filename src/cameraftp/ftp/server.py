from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


class FTPWorker:
    def __init__(
        self,
        on_file_received: Callable[[Path], None],
        passive_ports: list[int],
        masquerade_address: Optional[str] = None,
    ):

        class _Handler(FTPHandler):
            def on_file_received(self, file: str) -> None:
                on_file_received(Path(file))

        self.handler = _Handler
        self.handler.passive_ports = passive_ports  # type: ignore
        self.handler.masquerade_address = masquerade_address  # type: ignore

    def add_user(self, username: str, password: str, homedir: Path, perm: str):
        self.handler.authorizer.add_user(username, password, str(homedir), perm=perm)

    def worker(self, host: str, port: int):
        server = FTPServer((host, port), self.handler)
        server.serve_forever()


def parse_passive_ports(s: str) -> list[int]:
    a, b = s.split("-", 1)
    start = int(a.strip())
    end = int(b.strip())
    return list(range(start, end + 1))
