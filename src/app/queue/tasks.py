from __future__ import annotations

from pathlib import Path

from app.config.loader import load_config
from app.processing.decode_image import decode_image_to_float32
from app.processing.decode_raw import decode_raw_to_float32
from app.processing.encode import write_outputs
from app.processing.pipeline import apply_pipeline
from app.queue.celery_app import celery_app


@celery_app.task(name="photoftp.process_file")
def process_file(
    config_path: str, file_path: str, rule_index: int, input_index: int
) -> dict:
    cfg = load_config(Path(config_path))
    rule = cfg.rules[rule_index]
    inp = rule.input[input_index]

    src = Path(file_path)

    if inp.type == "raw":
        img = decode_raw_to_float32(src, inp.raw)
    else:
        img = decode_image_to_float32(src)

    img = apply_pipeline(img, rule.pipeline)

    out_dir = Path("data/output")
    write_outputs(img, rule.outputs, out_dir, src_path=src)

    return {
        "ok": True,
        "out_dir": str(out_dir),
    }
