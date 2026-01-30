from __future__ import annotations

from datetime import date
import logging
from pathlib import Path
from typing import Final
from trilobite.cli.runtimeflags import ConfigFlags
from trilobite.config.models import (
    AppConfig,
    CFGAnalysis,
    CFGDev,
    CFGMisc,
    CFGTickerService,
    CFGDataBase,
)
from trilobite.utils.paths import config_dir

logger = logging.getLogger(__name__)

#When adding new, remember to update:
#DEFAULTS
#CONFIG_TEMPLATE
#Add to a model
#Add model if not alreadyd one

CONFIG_FILENAME: Final[str] = "trilobite.conf"

DEFAULTS: Final[dict[str, str]] = {
    "dev" : "False",
    "debug" : "False",
    "dry_run" : "False",
    "consolelog" : "False",
    "default_date": "1975-01-01",
    "default_timedelta": "1",
    "dbname": "trilobite",
    "host": "/run/postgresql",
    "user": "none",
    "port": "5432",
    "stagger_requests": "True",
    "top_n": "20",
    "n_factors": "75",
    "min_days": "1260",
    "lookback": "60",
    "horizon": "1",
    "epochs": "10",
}

CONFIG_TEMPLATE: Final[str] = """\
# Trilobite configuration file
# Lines starting with # are comments.
# Inline comments are suppored: key = value # comment
# 
# Values are mostly strings; they are parsed into correct ypes by the app

# --- Dev settings ---
dev = False
debug = False
dry_run = False
consolelog = False

# --- TickerService Settings ---
default_date = 1975-01-01
default_timedelta = 1

# --- Database settings ---
dbname = trilobite
host = /run/postgresql
user = None
port = 5432

# --- Misc Settings ---
# The app will wait a small amount of time(1-2 seconds) between each request
# to avoid spamming the target with requests
stagger_requests = True

# --- Analysis Settings ---
top_n = 20
n_factors = 20
min_days = 1260
lookback = 60
horizon = 1
epochs = 10
"""

def _strip_inline_comment(line: str) -> str:
    """
    Removes inline comments starting with #, unless line already starts with #
    """
    if not line:
        return line
    if line.lstrip().startswith("#"):
        return ""
    return line.split("#", 1)[0].strip()

def _load_config_file(filepath: Path) -> dict[str, str]:
    """
    Loads the actual config file as a raw string key/value pairs

    Supports blank lines, full line comments, inline comments
    """
    cfg: dict[str, str] = {}

    with filepath.open("r", encoding="utf-8") as f:
        for raw in f:
            line = _strip_inline_comment(raw.strip())
            if not line:
                continue
            if "=" not in line:
                logger.warning("Ignoring invalid config line, missing '='")
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()

            if not key:
                logger.warning("Ignoring invalid config line, empty key")
                continue

            cfg[key] = val
    return cfg

def _generate_config_file(filepath: Path) -> None:
    """
    Generates a new config file if one doesn't exist, using default values
    """

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", encoding="utf-8") as f:
        f.write(CONFIG_TEMPLATE)

def _get_int(cfg: dict[str, str], key: str) -> int:
    raw = cfg.get(key, DEFAULTS[key]).strip()
    try:
        return int(raw)
    except ValueError:
        logger.warning(f"Invalid int for {key} = {raw}, defaulting to {DEFAULTS[key]}")
        return int(DEFAULTS[key])

def _get_str(cfg: dict[str, str], key: str) -> str:
    return cfg.get(key, DEFAULTS[key]).strip()

def _get_optional_str(cfg: dict[str, str], key: str) -> str | None:
    raw = _get_str(cfg, key)
    if raw == "" or raw.lower() in {"none", "null"}:
        return None
    return raw

def _get_bool(cfg: dict[str, str], key: str) -> bool:
    raw = cfg.get(key, DEFAULTS[key]).strip()
    try:
        return eval(raw)
    except NameError:
        logger.warning(f"Invalid bool for {key} = {raw}, defaulting to {DEFAULTS[key]}")
        return eval(DEFAULTS[key])

def load_config(runtimeflags: ConfigFlags) -> AppConfig:
    """
    Takes in a dict of strings(check on this later) that is then distributed
    among different config modules, they are stored in a common module AppConfig
    that is then passed back and sent to App, where App can distribute the
    submodules as it likes
    """
    logger.debug(f"Start ..")
    filepath = config_dir() / CONFIG_FILENAME

    if not filepath.is_file():
        logger.info("Config not found. Generating default config")
        _generate_config_file(filepath)

    cfg = _load_config_file(filepath)

    dev_cfg = CFGDev(
        dev=runtimeflags.dev if runtimeflags.dev is not None else _get_bool(cfg, "dev"),
        debug=runtimeflags.debug if runtimeflags.debug is not None else _get_bool(cfg, "debug"),
        dry_run=runtimeflags.dry_run if runtimeflags.dry_run is not None else _get_bool(cfg, "dry_run"),
        consolelog=runtimeflags.consolelog if runtimeflags.consolelog is not None else _get_bool(cfg, "consolelog"),
    )

    ticker_cfg = CFGTickerService(
        default_date=date.fromisoformat(cfg.get("default_date", DEFAULTS["default_date"])),
        default_timedelta=_get_int(cfg, "default_timedelta"),
    )

    db_cfg = CFGDataBase(
        dbname=_get_str(cfg, "dbname"),
        host=_get_str(cfg, "host"),
        user=_get_optional_str(cfg, "user"),
        port=_get_int(cfg, "port"),
    )

    misc_cfg = CFGMisc(
        stagger_requests=_get_bool(cfg, "stagger_requests"),
    )

    analysis_cfg = CFGAnalysis(
        top_n=runtimeflags.topn if runtimeflags.topn is not None else _get_int(cfg, "top_n"),
        n_factors=runtimeflags.n_factors if runtimeflags.n_factors is not None else _get_int(cfg, "n_factors"),
        min_days=runtimeflags.min_days if runtimeflags.min_days is not None else _get_int(cfg, "min_days"),
        lookback=runtimeflags.lookback if runtimeflags.lookback is not None else _get_int(cfg, "lookback"),
        horizon=runtimeflags.horizon if runtimeflags.horizon is not None else _get_int(cfg, "horizon"),
        epochs=runtimeflags.epochs if runtimeflags.epochs is not None else _get_int(cfg, "epochs"),
    )
    logger.info(f"Config loaded ..")
    return AppConfig(
        dev=dev_cfg,
        ticker=ticker_cfg,
        db=db_cfg,
        misc=misc_cfg,
        analysis=analysis_cfg,
    )
