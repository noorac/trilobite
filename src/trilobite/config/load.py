from __future__ import annotations

from datetime import date
from trilobite.config.models import (
    AppConfig,
    CFGTickerService,
    CFGDataBase,
)

def load_config(cfg: dict[str, str]) -> AppConfig:
    """
    Takes in a dict of strings(check on this later) that is then distributed
    among different config modules, they are stored in a common module AppConfig
    that is then passed back and sent to App, where App can distribute the
    submodules as it likes
    """

    ticker_cfg = CFGTickerService(
        default_date=date.fromisoformat(cfg.get("default_date", "1975-01-01")),
        default_timedelta=int(cfg.get("default_timedelta", 1)),
    )

    db_cfg = CFGDataBase(
        dbname=cfg.get("dbname", "trilobite"),
        host=cfg.get("host", "/run/postgresql"),
        user=cfg.get("user", None),
        port=int(cfg.get("port", 5432)),
    )

    return AppConfig(
        ticker=ticker_cfg,
        db=db_cfg,
    )
