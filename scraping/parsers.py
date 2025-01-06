#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: parsers.py
Description: Extracts and structures scraped data
Author: Kjetil Paulsen
Date: 2025-01-01
"""

# =========================
# Imports
# =========================
import os
import sys
import logging
import pandas as pd

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
def clean_hist_data(ticker,filepath) -> None:
    """
    Function that will grab history-data from ..data/raw and
    clean it and put it in data/processed. Argument passed
    should be the full file path:
    .../data/raw/<ticker>/<ticker>_hist.csv
    """
    logger.info(f"Starting parsers.clean_hist_data()...")
    print(filepath)
    print(filepath[:filepath.rfind("raw/"+ticker+"/"+ticker+"_")])
    processedpath = filepath[:filepath.rfind("raw/"+ticker+"/"+ticker+"_")]+"processed/"+ticker
    logger.info(f"Checking for ticker-folder at {processedpath}")
    if not os.path.exists(processedpath):
        logger.info(f"Folder does not exist, creating folder for ticker '{ticker}'")
        os.makedirs(processedpath)
    else:
        logger.info(f"Folder for ticker '{ticker}' already exists, continuing")
    processedfile = processedpath + "/" + ticker + "_history_cleaned.csv"
    df = pd.read_csv(filepath + "history.csv")
    # Remove empty cells
    df.dropna(inplace = True)
    df.to_csv(processedfile)
    logger.info(f"Finished parsers.clean_hist_data()...")
    return None

# =========================
# Main Function
# =========================
def main():
    """
    Main function to run the script.
    """
    logger.info("Starting parsers.main()...")
    # Example usage
    ticker = "GOOG"
    filepath = _ #insertfilepath
    clean_hist_data(ticker, filepath)
    logger.info(f"Finished running parsers.main()")

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
