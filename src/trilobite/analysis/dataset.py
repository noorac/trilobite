from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
import torch
from pandas import DataFrame
from torch.utils.data import Dataset


@dataclass(frozen=True)
class FactorDatasetSpec:
    """
    Dataset spec for factor-window -> next-day direction vector.

    Attributes
    ----------
    lookback:
        Number of factor timesteps in each input window.
    horizon:
        Prediction horizon in timesteps. horizon=1 means "tomorrow".
    """
    lookback: int = 60
    horizon: int = 1


def make_direction_labels(returns_wide: DataFrame, *, horizon: int = 1) -> DataFrame:
    """
    y[t] = 1 if return[t + horizon] > 0 else 0

    Output DataFrame has same columns as returns_wide (tickers).
    Last `horizon` rows are dropped.
    """
    _assert_matrix(returns_wide, name="returns_wide")
    if horizon <= 0:
        raise ValueError("horizon must be > 0")

    future = returns_wide.shift(-horizon)
    y = (future > 0.0).astype(np.float32)
    return y.iloc[:-horizon]


def _assert_matrix(df: DataFrame, *, name: str) -> None:
    if df.empty:
        raise ValueError(f"{name} is empty")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError(f"{name} index must be a DatetimeIndex")
    if df.isna().any().any():
        raise ValueError(f"{name} contains NaNs (v1 requires no NaNs)")


class FactorWindowDirectionDataset(Dataset[Tuple[torch.Tensor, torch.Tensor]]):
    """
    Each sample corresponds to a date t (after lookback warmup):

    - X: factor window ending at t, shape (lookback, k_factors)
    - y: direction vector for t+horizon, shape (n_tickers,)

    We align dates like this:
      X uses factors at dates [t-lookback+1, ..., t]
      y uses returns direction at date t (because labels are pre-shifted inside make_direction_labels)

    Implementation details:
    - We compute y_df = direction(returns shifted -horizon) and drop last horizon rows.
    - We align factors to y_df.index so both have same timeline.
    - For item idx:
        i = idx + lookback - 1  (index into aligned arrays)
        X = factors[i-lookback+1 : i+1]
        y = y[i]
    """

    def __init__(self, factors: DataFrame, returns_wide: DataFrame, spec: FactorDatasetSpec):
        _assert_matrix(factors, name="factors")
        _assert_matrix(returns_wide, name="returns_wide")

        if spec.lookback <= 0:
            raise ValueError("lookback must be > 0")
        if spec.horizon <= 0:
            raise ValueError("horizon must be > 0")

        # Labels: (T', N) where T' = T - horizon
        y_df = make_direction_labels(returns_wide, horizon=spec.horizon)

        # Align factors to the same dates (drop last horizon rows to match):
        if not factors.index.equals(returns_wide.index):
            raise ValueError("factors and returns_wide must have identical date index in v1")

        f_df = factors.loc[y_df.index]

        self._tickers = list(returns_wide.columns)
        self._factor_names = list(f_df.columns)
        self._dates = y_df.index

        self._lookback = spec.lookback

        # Convert to tensors
        self._X = torch.from_numpy(f_df.to_numpy(dtype=np.float32))     # (T', K)
        self._y = torch.from_numpy(y_df.to_numpy(dtype=np.float32))     # (T', N)

        # Need enough rows for at least 1 sample
        self._n_samples = len(self._dates) - (self._lookback - 1)
        if self._n_samples <= 0:
            raise ValueError(
                f"Not enough rows for lookback={spec.lookback} and horizon={spec.horizon}. "
                f"Need at least {spec.lookback + spec.horizon} rows total."
            )

    @property
    def tickers(self) -> list[str]:
        return self._tickers

    @property
    def factor_names(self) -> list[str]:
        return self._factor_names

    @property
    def dates(self) -> pd.DatetimeIndex:
        return self._dates

    def __len__(self) -> int:
        return self._n_samples

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        if idx < 0 or idx >= self._n_samples:
            raise IndexError(idx)

        i = idx + (self._lookback - 1)
        x = self._X[i - (self._lookback - 1) : i + 1, :]  # (lookback, K)
        y = self._y[i, :]                                  # (N,)
        return x, y

