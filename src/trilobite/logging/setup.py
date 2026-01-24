from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from trilobite.utils.paths import logs_dir

def setup_logging(level: int = logging.INFO) -> None:
    """
    Configures the logging for the entire application

    Sets the path for all future logs to logs/trilobite.log
    """
    log_file: Path = logs_dir() / "trilobite.log"
    history_file: Path = logs_dir() / "trilobite_history.log"

    #create the parent logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    #remove existing handlers from logging.basicConfig
    root_logger.handlers.clear()

    formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
    )

    history_handler = RotatingFileHandler(
            history_file,
            maxBytes=10_000_000,
            backupCount=5,
            encoding="utf-8",
    )
    history_handler.setLevel(level)
    history_handler.setFormatter(formatter)
    root_logger.addHandler(history_handler)

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    return None
