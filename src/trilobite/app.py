from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

class App:
    """
    The main app
    """
    def __init__(self) -> None:
        logger.info("Initializing ..")

        return None

    def run(self, stdscr: "curses._CursesWindow") -> None:
        """
        Starting up the app system
        """
        logger.info("Starting curses..")
        return None

