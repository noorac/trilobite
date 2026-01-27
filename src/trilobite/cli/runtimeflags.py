from __future__ import annotations
from dataclasses import dataclass
from os import wait

@dataclass(frozen=True)
class RuntimeFlags:
    dev: bool = False
    debug: bool = False
    dry_run: bool = False
    curses: bool = False

@dataclass
class CLIFlags:
    updateall: bool = False
