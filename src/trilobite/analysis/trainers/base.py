from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


@dataclass(frozen=True)
class Prediction:
    """
    Prediction for a single feature date.

    Attributes
    ----------
    date:
        The last date used in the feature window.
    probs_up:
        Series indexed by ticker with probability in [0,1] for "up tomorrow".
    """
    date: pd.Timestamp
    probs_up: pd.Series

    def ranked(self, top_n: int | None = None) -> pd.Series:
        s = self.probs_up.sort_values(ascending=False)
        return s if top_n is None else s.head(top_n)


class Trainer(Protocol):
    #def fit(self, returns_wide, *, factors=None) -> None: ...
    def fit(self, returns_wide) -> None: ...
    def predict_latest(self, returns_wide, *, factors=None) -> Prediction: ...

