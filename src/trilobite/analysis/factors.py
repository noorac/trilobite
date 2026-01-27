from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame


@dataclass(frozen=True)
class FactorSpec:
    """
    Specification for the factor model.

    Attributes
    ----------
    n_factors:
        Number of PCA components to keep.
    standardize:
        If True, standardize each ticker return series by its training-period
        std dev (and mean-center always). This can help when tickers have
        different volatilities. For v1, we keep it simple but include it.
    """
    n_factors: int = 64
    standardize: bool = False


class PCAReturnFactors:
    """
    PCA factor model for cross-sectional daily returns.

    Fits PCA on returns matrix R of shape (T, N), where:
    - T = number of dates
    - N = number of tickers

    Transform produces factor time series Z of shape (T, K),
    where K = n_factors.

    Notes
    -----
    - Uses SVD on mean-centered (and optionally standardized) returns.
    - Stores parameters needed to transform new data consistently.
    """

    def __init__(self, spec: Optional[FactorSpec] = None) -> None:
        self.spec = spec or FactorSpec()
        if self.spec.n_factors <= 0:
            raise ValueError("n_factors must be > 0")

        self._tickers: list[str] = []
        self._mean: np.ndarray | None = None           # (N,)
        self._scale: np.ndarray | None = None          # (N,)
        self._components: np.ndarray | None = None     # (K, N)

        self._fitted: bool = False

    @property
    def tickers(self) -> list[str]:
        return self._tickers

    @property
    def n_factors(self) -> int:
        if self._components is None:
            return self.spec.n_factors
        return int(self._components.shape[0])

    def fit(self, returns_wide: DataFrame) -> "PCAReturnFactors":
        _assert_returns_matrix(returns_wide)

        self._tickers = list(returns_wide.columns)
        X = returns_wide.to_numpy(dtype=np.float64, copy=True)  # (T, N)

        mean = X.mean(axis=0)  # (N,)
        Xc = X - mean

        if self.spec.standardize:
            scale = Xc.std(axis=0, ddof=1)
            # Avoid division by zero for ultra-flat series
            scale[scale == 0.0] = 1.0
            Xc = Xc / scale
            self._scale = scale
        else:
            self._scale = np.ones(Xc.shape[1], dtype=np.float64)

        # SVD: Xc = U S Vt, where Vt rows are principal directions
        # We want top K rows of Vt -> (K, N)
        U, S, Vt = np.linalg.svd(Xc, full_matrices=False)

        K = min(self.spec.n_factors, Vt.shape[0])
        comps = Vt[:K, :]  # (K, N)

        self._mean = mean
        self._components = comps
        self._fitted = True
        return self

    def transform(self, returns_wide: DataFrame) -> DataFrame:
        if not self._fitted:
            raise RuntimeError("PCAReturnFactors is not fitted. Call fit() first.")
        _assert_returns_matrix(returns_wide)

        if list(returns_wide.columns) != self._tickers:
            raise ValueError(
                "Ticker columns do not match fitted factor model. "
                "Ensure consistent ticker set and ordering."
            )

        X = returns_wide.to_numpy(dtype=np.float64, copy=True)
        mean = _require(self._mean)
        scale = _require(self._scale)
        comps = _require(self._components)  # (K, N)

        Xc = (X - mean) / scale  # (T, N)

        # Project into factor space: Z = Xc @ comps.T -> (T, K)
        Z = Xc @ comps.T

        cols = [f"F{i+1:02d}" for i in range(Z.shape[1])]
        return pd.DataFrame(Z.astype(np.float32), index=returns_wide.index, columns=cols)

    def fit_transform(self, returns_wide: DataFrame) -> DataFrame:
        return self.fit(returns_wide).transform(returns_wide)


def _require(x):
    if x is None:
        raise RuntimeError("Internal state missing; factor model not fitted correctly.")
    return x


def _assert_returns_matrix(df: DataFrame) -> None:
    if df.empty:
        raise ValueError("returns matrix is empty")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("returns matrix index must be a DatetimeIndex")
    if df.shape[1] < 2:
        raise ValueError("returns matrix must have at least 2 tickers (columns)")
    if df.isna().any().any():
        raise ValueError(
            "returns matrix contains NaNs. For v1, drop tickers/dates with NaNs first."
        )

