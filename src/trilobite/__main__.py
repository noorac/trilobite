from __future__ import annotations

import logging
import sys
from typing import NoReturn

from trilobite.app import App
from trilobite.cli.cli import parse_args
from trilobite.cli.runtimeflags import CliFlags
from trilobite.config.config import AppConfig
from trilobite.logging.setup import setup_logging

def _headless_main(cfg: AppConfig, cliflags: CliFlags) -> None:
    """
    Starts the application in headless mode
    """
    app = App(cfg)
    app.run_headless(cliflags)

def main() -> NoReturn:
    """
    Entrypoint:
    - Starts logging
    - Starts headless
    - Handles fatal errors
    """
    cfg, cliflags = parse_args(sys.argv[1:])
    level = logging.DEBUG if cfg.dev.debug else logging.INFO
    #minimal fallback logging to stderr if unable to start setup_logging()
    logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("trilobite")

    try:
        setup_logging(level=level, console=cfg.dev.consolelog)
        _headless_main(cfg, cliflags)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception:
        # Any uncaught exceptions are logged before dying
        logger.exception("---FATAL ERROR---")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
