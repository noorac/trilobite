from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfigFlags:
    #Dev related
    dev: bool = False
    debug: bool = False
    dry_run: bool = False
    consolelog: bool = False
    #Settings
    default_date: int | None = None
    default_timedelta: int | None = None
    topn: int | None = None # 20
    n_factors: int | None = None # 20
    min_days: int | None = None # 1260
    lookback: int | None = None # 60
    horizon: int | None = None # 1
    epochs: int | None = None # 10

@dataclass
class CliFlags:
    #Commands
    updateall: bool = False
    train_nn: bool = False


