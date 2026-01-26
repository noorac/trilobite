from __future__ import annotations

import curses
import logging
import sys
from typing import NoReturn

from trilobite.app import App
from trilobite.config.load import load_config
from trilobite.logging.setup import setup_logging

def _headless_main(argv: list[str]) -> None:
    """
    Starts the application in headless mode
    """
    cfg = load_config()
    app = App(cfg)
    app.run_headless(argv)

def _curses_main(stdscr: "curses._CursesWindow") -> None:
    """
    Runs inside curses.wrapper() and starts the application in curses mode
    """
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()

    stdscr.clear()
    stdscr.refresh()

    cfg = load_config()
    app = App(cfg)
    app.run_curses(stdscr)


def main() -> NoReturn:
    """
    Entrypoint:
    - Starts logging
    - Starts headless/curses
    - Handles fatal errors
    """
    argv = sys.argv[1:]
    #Debug
    debug = "--debug" in argv
    level = logging.DEBUG if debug else logging.INFO
    #minimal fallback logging to stderr if unable to start setup_logging()
    logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("trilobite")

    #Curses
    run_curses = "--curses" in argv

    try:
        setup_logging(level=level)
        if run_curses:
            curses.wrapper(_curses_main)
        else:
            _headless_main(argv)
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
