from __future__ import annotations

import curses
import logging
import sys
from typing import NoReturn

from trilobite.app import build_app
from trilobite.logging.setup import setup_logging

def _curses_main(stdscr: "curses._CursesWindow") -> None:
    """
    Runs inside curses.wrapper() and starts the actual application
    """
    app = build_app()
    app.run(stdscr)

def main() -> NoReturn:
    """
    Entrypoint:
    - Starts logging
    - Starts curses
    - Handles fatal errors
    """
    try:
        setup_logging()
        curses.wrapper(_curses_main)
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Interrupted by user")
        sys.exit(130)
    except Exception:
        # Any uncaught exceptions are logged before dying
        logging.getLogger(__name__).exception("Fatal error")
        sys.exit(1)

    sys.exit(0)

