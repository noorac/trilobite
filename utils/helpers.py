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
import inspect
import string

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

def log_function_details(func):
    def wrapper(*args, **kwargs):
        # Get the module name
        module_name = func.__module__
        if module_name == "__main__":
            module_name = os.path.splitext(os.path.basename(inspect.stack()[-1].filename))[0]
        # Get the fully qualified name (class name + function name, if applicable)
        qualified_name = func.__qualname__
        # Log before running the function
        logger.info(f"Starting {module_name}.{qualified_name}(*{args}, **{kwargs})")
        # Run the original function
        result = func(*args, **kwargs)
        # Log after running the function
        logger.info(f"Finished {module_name}.{qualified_name}(*{args}, **{kwargs})")
        return result
    return wrapper

@log_function_details
def check_valid_ticker(ticker) -> bool:
    valid = True
    try:
        for a in ticker:
            if a.lower() not in list(string.ascii_letters[:26]):
                raise ValueError
    except ValueError:
        logger.error(f"ValueError: Not a valid ticker ...")
        valid = False
    return valid

@log_function_details
def checkdirs(folderpath) -> None:
    """
    Function that takes a path to a folder as argument, and
    if the folder exists, it does nothing, but if it doesn't 
    exist it creates a folder at the location.
    """
    #logger.info(f"Checking for ticker-folder at {folderpath}")
    if not os.path.exists(folderpath):
        #logger.info(f"Folder does not exist, creating folder at {folderpath}'")
        logger.info(f"Creating folder at {folderpath}'")
        os.makedirs(folderpath)
    else:
        logger.info(f"Folder exist ... continuing")
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
