from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AnalysisSettings:
    min_days: int = 252 * 5
    lookback: int = 60
    horizon: int = 1
