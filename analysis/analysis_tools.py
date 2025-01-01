#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: analysis_tools.py
Description: Core analysis algorithms
Author: Kjetil Paulsen
Date: 2025-01-01
"""

# =========================
# Imports
# =========================
#import os
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
def example_function(param1, param2):
    """
    Example function that does something.
    Args:
        param1 (type): Description of param1.
        param2 (type): Description of param2.
    Returns:
        type: Description of the return value.
    """
    logger.info(f"Running example_function with {param1=} and {param2=}")
    return param1 + param2

# =========================
# Main Function
# =========================
def main():
    """
    Main function to run the script.
    """
    logger.info("Starting the script...")
    # Example usage
    result = example_function(1, 2)
    logger.info(f"Result: {result}")

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
