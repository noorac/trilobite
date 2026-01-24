from __future__ import annotations

import curses
import logging
import sys
from typing import NoReturn

from trilobite.app import App
from trilobite.config.load import load_config
from trilobite.logging.setup import setup_logging

def _curses_main(stdscr: "curses._CursesWindow") -> None:
    """
    Runs inside curses.wrapper() and starts the actual application
    """
    cfg = load_config({})
    app = App(cfg)
    app.run(stdscr)


def main() -> NoReturn:
    """
    Entrypoint:
    - Starts logging
    - Starts curses
    - Handles fatal errors
    """
    argv = sys.argv[1:]
    debug = "--debug" in argv
    level = logging.DEBUG if debug else logging.INFO

    #minimal fallback logging to stderr if unable to start setup_logging()
    logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("trilobite")

    try:
        setup_logging(level=level)
        curses.wrapper(_curses_main)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception:
        # Any uncaught exceptions are logged before dying
        logger.exception("Fatal error")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
