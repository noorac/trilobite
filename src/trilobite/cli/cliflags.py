from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CLIFlags:
    updateall: bool = False
    train_nn: bool = False

    topn: int | None = None
    n_factors: int = 20
    min_days: int = 252 * 5
    lookback: int = 60
    horizon: int = 1
    epochs: int = 10

