from __future__ import annotations

import subprocess
from pathlib import Path


class Processor:
    def __init__(self, bin_path: str):
        self.bin_path = bin_path

    def run(
        self,
        input_path: Path,
        output_path: Path,
        inputs: list[str],
        outputs: list[str],
    ) -> Path:
        cmd = [self.bin_path, *inputs, str(input_path), *outputs, str(output_path)]
        subprocess.run(cmd, check=True)
        return output_path
