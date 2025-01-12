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
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
import analysis.stockobject
import utils.helpers

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

@utils.helpers.log_function_details
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
         logger.info(f"{sys.argv[1]=}")
    except IndexError:
        logger.error(f"IndexError: No argument was given, exiting...")
        sys.exit(1)
    if not utils.helpers.check_valid_ticker(sys.argv[1]):
        sys.exit(1)
    ticker = sys.argv[1].upper()
    logger.info(f"Starting main ...")
    currentpath = get_currentpath()
    scraping.scraper.dl_data(ticker,currentpath)
    scraping.parsers.clean_hist_data(ticker,currentpath)
    stock = analysis.stockobject.Stockobject(ticker, currentpath)
    # Menu-option, create more robust version later in issue #19
    cont = True
    while cont:
        print(f"1. Create plot using closing values, 0. quit")
        choise = input("Your choise: ")
        if int(choise) == 0:
            cont = False
        if int(choise) == 1:
            stock.show_graph()


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
