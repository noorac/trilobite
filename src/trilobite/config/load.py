from __future__ import annotations

from datetime import date
import logging
from pathlib import Path
from typing import Final
from trilobite.config.models import (
    AppConfig,
    CFGTickerService,
    CFGDataBase,
)
from trilobite.utils.paths import config_dir

logger = logging.getLogger(__name__)

CONFIG_FILENAME: Final[str] = "trilobite.conf"

DEFAULTS: Final[dict[str, str]] = {
    "default_date": "1975-01-01",
    "default_timedelta": "1",
    "dbname": "trilobite",
    "host": "/run/postgresql",
    "user": "none",
    "port": "5432",
}

CONFIG_TEMPLATE: Final[str] = """\
# Trilobite configuration file
# Lines starting with # are comments.
# Inline comments are suppored: key = value # comment
# 
# Values are mostly strings; they are parsed into correct ypes by the app

# --- TickerService Settings ---
default_date = 1975-01-01
default_timedelta = 1

# --- Database settings ---
dbname = trilobite
host = /run/postgresql
user = None
port = 5432
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

def load_config() -> AppConfig:
    """
    Takes in a dict of strings(check on this later) that is then distributed
    among different config modules, they are stored in a common module AppConfig
    that is then passed back and sent to App, where App can distribute the
    submodules as it likes
    """
    filepath = config_dir() / CONFIG_FILENAME

    if not filepath.is_file():
        logger.info("Config not found. Generating default config")
        _generate_config_file(filepath)

    cfg = _load_config_file(filepath)

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

    return AppConfig(
        ticker=ticker_cfg,
        db=db_cfg,
    )
