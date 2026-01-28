from __future__ import annotations

import curses
import logging
import sys
from typing import NoReturn

from trilobite.app import App
from trilobite.cli.cli import parse_args
from trilobite.cli.runtimeflags import RuntimeFlags
from trilobite.cli.cliflags import CLIFlags 
from trilobite.config.load import load_config
from trilobite.logging.setup import setup_logging

def _headless_main(cliflags: CLIFlags, runtimeflags: RuntimeFlags) -> None:
    """
    Starts the application in headless mode
    """
    cfg = load_config(runtimeflags)
    app = App(cfg, runtimeflags)
    app.run_headless(cliflags)

def _curses_main(stdscr: "curses._CursesWindow", runtimeflags: RuntimeFlags) -> None:
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

    cfg = load_config(runtimeflags)
    app = App(cfg, runtimeflags)
    app.run_curses(stdscr)


def main() -> NoReturn:
    """
    Entrypoint:
    - Starts logging
    - Starts headless/curses
    - Handles fatal errors
    """
    runtimeflags,cliflags, ns = parse_args(sys.argv[1:])
    level = logging.DEBUG if runtimeflags.debug else logging.INFO
    #minimal fallback logging to stderr if unable to start setup_logging()
    logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("trilobite")

    try:
        setup_logging(level=level, console=runtimeflags.consolelog)
        if runtimeflags.curses:
            curses.wrapper(_curses_main,runtimeflags)
        else:
            _headless_main(cliflags,runtimeflags)
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
