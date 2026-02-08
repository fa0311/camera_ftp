from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from wcmatch import glob

from cameraftp.config.models import Rule


@dataclass(frozen=True)
class MatchResult:
    rule: Rule


def match_all(
    rules: list[Rule],
    path: Path,
) -> list[MatchResult]:
    results: list[MatchResult] = []
    for rule in rules:
        for pat in rule.input_globs:
            if glob.globmatch(path, pat, flags=glob.GLOBSTAR):
                results.append(MatchResult(rule=rule))
                break
    return results
