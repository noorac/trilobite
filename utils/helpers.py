#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: helpers.py
Description: Reusable functions and tools
Author: Kjetil Paulsen
Date: 2025-01-01
"""

# =========================
# Imports
# =========================

import os
import sys
import logging

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

def checkdirs(folderpath) -> None:
    """
    Function that takes a path to a folder as argument, and
    if the folder exists, it does nothing, but if it doesn't 
    exist it creates a folder at the location.
    """
    logger.info(f"Checking for ticker-folder at {folderpath}")
    if not os.path.exists(folderpath):
        logger.info(f"Folder does not exist, creating folder at {folderpath}'")
        os.makedirs(folderpath)
    else:
        logger.info(f"Folder exist at {folderpath} .. continuing")
    return None

# =========================
# Main Function
# =========================

def main() -> None:
    """
    Main function to run the script.
    """
    logger.info(f"Starting helpers.main()...")
    logger.info(f"Ending helpers.main()...")
    return None

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
