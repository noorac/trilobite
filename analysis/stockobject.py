#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: stockobject.py
Description: Contains the class stock. It will be an object of the stock,
and load and contain data about the stock itself.
Author: Kjetil Paulsen
Date: 2025-01-10
"""

# =========================
# Imports
# =========================
import os
import sys
import logging
import pandas as pd
#from analysis import visualizations
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

# =========================
# Classes
# =========================

class Stockobject:
    @utils.helpers.log_function_details
    def __init__(self, ticker, currentpath) -> None:
        self.ticker = ticker
        self.currentpath = currentpath
        self.rawpath = currentpath + "data/raw/" + ticker + "/" + ticker
        self.processedpath = currentpath + "data/processed/" + ticker + "/" + ticker
        self.historypath = self.processedpath + "_history_cleaned.csv"
        self.plotpath = self.processedpath + "_saveplot.png"
        self.history = pd.read_csv(self.historypath)
        return None

# =========================
# Main Function
# =========================
def main():
    """
    Main function to run the script.
    """
    logger.info("Starting stockobject.main()...")
    logger.info("Finished stockobject.main()...")

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

