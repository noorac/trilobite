#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: scraper.py
Description: Fetches financial data from web sources
Author: Kjetil Paulsen
Date: 2025-01-01
"""

# =========================
# Imports
# =========================
import os
import sys
import logging
import yfinance as yf
import json as js

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
def dl_data(arg) -> None:
    """
    Downloads and stores data, takes a ticker symbol as argument
    """
    logger.info(f"Running dl_data with {arg=}")
    # Initialize the download
    dt = yf.Ticker(arg)
    # Get path of this script
    currentpath = os.path.realpath(__file__)
    # Change to data/raw folder
    folderpath = currentpath[:currentpath.rfind("scraping/scraper.py")] + "data/raw/" + arg
    #folderpath = folderpath + "data/raw/" + arg
    logger.info(f"Checking for ticker-folder at {folderpath}")
    if not os.path.exists(folderpath):
        logger.info(f"Folder does not exist, creating folder for ticker '{arg}'")
        os.makedirs(folderpath)
    else:
        logger.info(f"Folder for ticker '{arg}' already exists, continuing")
    logger.info(f"Finished dl_data with {arg=}")
    filepath = folderpath + "/" + arg + "_"
    #Save CSV formats
    # History
    hist = dt.history(period = 'max')
    hist.to_csv(filepath + "history.csv")
    #Balance Sheet
    bal_she = dt.balance_sheet
    bal_she.to_csv(filepath + "balance_sheet.csv")
    #Quarterly
    qtrl = dt.quarterly_income_stmt
    qtrl.to_csv(filepath + "quarterly.csv")
    # Save JSON formats
    # Info
    with open(filepath + "info.json", "w") as info_json:
        js.dump(dt.info, info_json)
    info_json.close()
    print(dt.calendar)
    with open(filepath + "calendar.json", "w") as calendar_json:
        js.dump(dt.calendar, calendar_json, default=str)
    calendar_json.close()
    return None

# =========================
# Main Function
# =========================
def main() -> None:
    """
    Main function to run the script.
    """
    logger.info("Starting the script...")
    arg = "GOOG"
    dl_data(arg)
    #logger.info(f"Result: {result}")

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
