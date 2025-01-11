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
def clean_hist_data(ticker,currentpath) -> None:
    """
    Function that will grab history-data from ..data/raw and
    clean it and put it in data/processed. Argument passed
    should be the full file path:
    .../data/raw/<ticker>/<ticker>_hist.csv
    """
    # Create path to data/processed/ticker folder
    folderpath = currentpath + "data/processed/" + ticker
    # Check if the folder exists and creat if it doesn't
    utils.helpers.checkdirs(folderpath)
    # Create path for filenames
    processedfile = folderpath + "/" + ticker + "_history_cleaned.csv"
    # Read history data
    df = pd.read_csv(currentpath+ "data/raw/"+ ticker + "/"+ ticker + "_history.csv")
    # Remove empty cells
    df.dropna(inplace = True)
    # Save history data
    df.to_csv(processedfile)
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
    currentpath = _ #insertcurrentpath
    clean_hist_data(ticker, currentpath)
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
