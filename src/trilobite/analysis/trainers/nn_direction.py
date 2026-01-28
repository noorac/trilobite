from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pandas import DataFrame
from torch.utils.data import DataLoader
from tqdm import tqdm

from trilobite.analysis.dataset import FactorDatasetSpec, FactorWindowDirectionDataset
from trilobite.analysis.factors import FactorSpec, PCAReturnFactors
from trilobite.analysis.trainers.base import Prediction

logger = logging.getLogger(__name__)

class _FactorGRUToUniverse(nn.Module):
    """
    Input:  (B, T, K)  factor windows
    Output: (B, N)     logits for each ticker
    """

    def __init__(self, n_factors: int, hidden_size: int, num_layers: int, n_tickers: int) -> None:
        super().__init__()
        self.gru = nn.GRU(
            input_size=n_factors,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
        )
        self.head = nn.Linear(hidden_size, n_tickers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.gru(x)      # (B, T, H)
        h = out[:, -1, :]         # (B, H)
        logits = self.head(h)     # (B, N)
        return logits


@dataclass
class NNDirectionsConfig:
    # factor model
    n_factors: int = 64
    standardize: bool = False

    # dataset
    lookback: int = 60
    horizon: int = 1

    # training
    epochs: int = 10
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4

    # model
    hidden_size: int = 128
    num_layers: int = 1

    # runtime
    device: str = "cpu"


class NNDirectionsTrainer:
    """
    Cross-sectional lead/lag model:

      returns (all tickers) -> PCA factors -> GRU over factor history -> probs for each ticker up tomorrow

    Input: returns_wide (T, N)
    Output: probabilities per ticker for next-day direction
    """

    def __init__(self, cfg: Optional[NNDirectionsConfig] = None) -> None:
        self.cfg = cfg or NNDirectionsConfig()
        self._factor_model: PCAReturnFactors | None = None
        self._model: _FactorGRUToUniverse | None = None
        self._tickers: list[str] = []

    @property
    def tickers(self) -> list[str]:
        return self._tickers

    def fit(self, returns_wide: DataFrame) -> None:
        if returns_wide.empty:
            raise ValueError("returns_wide is empty")
        if returns_wide.isna().any().any():
            raise ValueError("returns_wide contains NaNs (v1 requires no NaNs)")

        self._tickers = list(returns_wide.columns)
        n_tickers = len(self._tickers)

        # 1) Fit factor model on full training period returns
        factor_spec = FactorSpec(n_factors=self.cfg.n_factors, standardize=self.cfg.standardize)
        fm = PCAReturnFactors(factor_spec).fit(returns_wide)
        factors = fm.transform(returns_wide)  # (T, K)
        logger.info(f"factors.shape={factors.shape}, fm.n_factors={fm.n_factors}")

        # 2) Dataset
        ds_spec = FactorDatasetSpec(lookback=self.cfg.lookback, horizon=self.cfg.horizon)
        ds = FactorWindowDirectionDataset(factors=factors, returns_wide=returns_wide, spec=ds_spec)
        loader = DataLoader(ds, batch_size=self.cfg.batch_size, shuffle=True, drop_last=False)

        # 3) Model
        device = torch.device(self.cfg.device)
        model = _FactorGRUToUniverse(
            n_factors=fm.n_factors,
            hidden_size=self.cfg.hidden_size,
            num_layers=self.cfg.num_layers,
            n_tickers=n_tickers,
        ).to(device)

        opt = torch.optim.AdamW(model.parameters(), lr=self.cfg.lr, weight_decay=self.cfg.weight_decay)
        loss_fn = nn.BCEWithLogitsLoss()

        # 4) Train
        # model.train()
        # for _epoch in range(1, self.cfg.epochs + 1):
        #     for x, y in loader:
        #         # x: (B, lookback, K)
        #         # y: (B, N)
        #         x = x.to(device)
        #         y = y.to(device)
        #
        #         opt.zero_grad(set_to_none=True)
        #         logits = model(x)
        #         loss = loss_fn(logits, y)
        #         loss.backward()
        #         opt.step()
        model.train()
        for _epoch in range(1, self.cfg.epochs + 1):
            #Must remove pbar if using something else than terminal, see above
            #for clean without progerss updates.
            pbar= tqdm(loader, desc=f"Train epoch {_epoch}/{self.cfg.epochs}", leave=False)
            for x, y in pbar:
                # x: (B, lookback, K)
                # y: (B, N)
                x = x.to(device)
                y = y.to(device)

                opt.zero_grad(set_to_none=True)
                logits = model(x)
                loss = loss_fn(logits, y)
                loss.backward()
                opt.step()
                pbar.set_postfix(loss=float(loss.detach().cpu()))

        self._factor_model = fm
        self._model = model

    @torch.no_grad()
    def predict_latest(self, returns_wide: DataFrame) -> Prediction:
        """
        Predict next-day up probabilities using the latest lookback window.

        Important:
        - uses the factor model fitted during training
        - requires the same tickers/column order as training
        """
        if self._model is None or self._factor_model is None:
            raise RuntimeError("Trainer not fitted. Call fit() first.")

        if list(returns_wide.columns) != self._tickers:
            raise ValueError("returns_wide tickers differ from training tickers/order.")

        if returns_wide.isna().any().any():
            raise ValueError("returns_wide contains NaNs (v1 requires no NaNs)")

        lookback = self.cfg.lookback
        if len(returns_wide) < lookback + 1:
            raise ValueError(f"Need at least {lookback + 1} rows of returns to predict latest.")

        # Transform all returns to factors, then take last lookback factor rows
        factors = self._factor_model.transform(returns_wide)
        window = factors.iloc[-lookback:, :]  # (lookback, K)

        x = torch.from_numpy(window.to_numpy(dtype=np.float32)).unsqueeze(0)  # (1, T, K)

        device = torch.device(self.cfg.device)
        x = x.to(device)

        self._model.eval()
        logits = self._model(x).squeeze(0)  # (N,)
        probs = torch.sigmoid(logits).detach().cpu().numpy()

        probs_s = pd.Series(probs, index=self._tickers, name="p_up")
        pred_date = pd.Timestamp(returns_wide.index[-1])
        return Prediction(date=pred_date, probs_up=probs_s)

