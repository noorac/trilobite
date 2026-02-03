from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfigFlags:
    #Dev related
    dev: bool | None = None
    debug: bool | None = None
    dry_run: bool | None = None
    consolelog: bool | None = None
    #Settings
    default_date: int | None = None
    default_timedelta: int | None = None
    topn: int | None = None # 20
    n_factors: int | None = None # 20
    min_days: int | None = None # 1260
    lookback: int | None = None # 60
    horizon: int | None = None # 1
    epochs: int | None = None # 10
    period: str | None = None # 30d
    ticker: str | None = None # AAPL

@dataclass
class CliFlags:
    #Commands
    updateall: bool = False
    train_nn: bool = False
    display_graph: bool = False


