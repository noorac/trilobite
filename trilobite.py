#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: trilobite.py
Description: Main program
Author: Kjetil Paulsen
Date: 2025-01-01
"""

# =========================
# Imports
# =========================
import os
import sys
import logging
import string
import scraping.scraper
import scraping.parsers

# =========================
# Constants
# =========================
VERSION = "1.0.0"
LOG_FILE = "script.log"

# =========================
# Logger Configuration
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =========================
# Helper Functions
# =========================

def get_currentpath() -> str:
    currentpath = os.path.realpath(__file__)
    currentpath = currentpath[:currentpath.rfind("trilobite.py")]
    logger.info(f"{currentpath=}")
    return currentpath
# =========================
# Main Function
# =========================
def main():
    """
    Main function to run the script.
    """
    #Check if argument was given, and check if it is only letters
    try:
        for a in sys.argv[1]:
            if a.lower() not in list(string.ascii_letters[:26]):
                raise ValueError
    except IndexError:
        logger.error(f"IndexError: No argument was given, exiting...")
        sys.exit(1)
    except ValueError:
        logger.error(f"ValueError: Not a letter, exiting...")
        sys.exit(1)
    ticker = sys.argv[1].upper()
    logger.info(f"Starting main ...")
    currentpath = get_currentpath()
    scraping.scraper.dl_data(ticker,currentpath)
    scraping.parsers.clean_hist_data(ticker,currentpath)


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Script interrupted by the user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)
