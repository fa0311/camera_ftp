from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from wcmatch import glob

from app.config.models import AppConfig, Input, Rule


@dataclass(frozen=True)
class MatchResult:
    rule_index: int
    input_index: int
    rule: Rule
    input: Input


def match_all(config: AppConfig, path: Path) -> List[MatchResult]:
    s = path.as_posix().lower()

    results: List[MatchResult] = []
    for ri, rule in enumerate(config.rules):
        for ii, inp in enumerate(rule.input):
            for pat in inp.path_globs:
                if glob.globmatch(s, pat.lower(), flags=glob.GLOBSTAR):
                    results.append(
                        MatchResult(rule_index=ri, input_index=ii, rule=rule, input=inp)
                    )
                    break
    return results
