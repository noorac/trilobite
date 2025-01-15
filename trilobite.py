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
import analysis.visualizations
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

@utils.helpers.log_function_details
def print_menu(ticker) -> None:
    # Header 
    print(f"Trilobite:")
    # What ticker is currently the active one
    # Also one space
    print(f"Current stock: {ticker}\n")
    # Item one, change ticker
    print(f"1) Change ticker: ")
    # Item two, 
    print(f"2) Show historial graph: \n")
    # Quit
    print(f"0) Quit: \n")
    return None

def menu_answer() -> int:
    ans = input(f"Option: ")
    try:
        if int(ans) not in [0,1,2]:
            print(f"Not an option")
            menu_answer()
    except ValueError:
        print(f"Not an integer")
        menu_answer()
    return int(ans)

def menu_cont(choise, ticker, currentpath) -> bool:
    # Change ticker:
    if choise == 1:
        print(f"This option comes later")
        return True
    if choise == 2:
        #This option should become a submenu in the future
        stock = analysis.stockobject.Stockobject(ticker, currentpath)
        analysis.visualizations.show_graph(stock)
        return True
    if choise == 0:
        return False
    return True



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
    # Menu-option, create more robust version later in issue #19
    cont = True
    while cont:
        utils.helpers.clear_screen()
        print_menu(ticker)
        ans = menu_answer()
        cont = menu_cont(ans, ticker, currentpath)


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
