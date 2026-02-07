from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from wcmatch import glob

from photoftp.config.models import Input, Rule


@dataclass(frozen=True)
class MatchResult:
    rule: Rule
    input: Input


def match_all(
    rules: list[Rule],
    path: Path,
) -> List[MatchResult]:
    results: List[MatchResult] = []
    for rule in rules:
        for inp in rule.input:
            for pat in inp.path_globs:
                if glob.globmatch(path, pat.lower(), flags=glob.GLOBSTAR):
                    results.append(MatchResult(rule=rule, input=inp))
                    break
    return results
