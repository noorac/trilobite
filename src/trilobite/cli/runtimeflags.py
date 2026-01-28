from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeFlags:
    dev: bool = False
    debug: bool = False
    dry_run: bool = False
    consolelog: bool = False

