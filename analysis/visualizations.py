#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: visualizations.py
Description: Functions for plotting data trends
Author: Kjetil Paulsen
Date: 2025-01-01
"""

# =========================
# Imports
# =========================
import os
import sys
import logging
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
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
def show_graph(temppath,date, open, close, high, low, volume) -> None:
    """
    Function will display a graph of the stock
    """
    max_value = high.max()
    fig, ax1 = plt.subplots(figsize=(10,5))
    # Primary y-axis for stock prices
    ax1.plot(date, open, label="Open", linestyle="--", color="blue", alpha=0.6)
    ax1.plot(date, high, label="High", linestyle="--", color="green", alpha=0.6)
    ax1.plot(date, low, label="Low", linestyle="--", color="red", alpha=0.6)
    ax1.plot(date, close, label="Close", linewidth=2, color="black")  # Thicker line for Close
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Stock Price")
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle="--", alpha=0.5)
    # Set maxlimits on y-axis, and give a bit of breathing room
    ax1.set_ylim(0, max_value*1.15)
    
    # Secondary y-axis for Volume
    # ax2 = ax1.twinx()
    # ax2.bar(date, volume, label="Volume", color="orange", alpha=0.3, width=1)
    # ax2.set_ylabel("Volume")
    # ax2.legend(loc="upper right")
    ax2 = ax1.twinx()
    max_volume = volume.max()
    max_price = max(high.max(), close.max())  # Get the max stock price
    scaled_volume = volume * (max_price / max_volume)  # Scale volume to match stock price range
    ax2.bar(date, scaled_volume, label="Volume (scaled)", color="orange", alpha=0.3, width=1)
    ax2.set_ylabel("Volume (scaled)")
    ax2.legend(loc="upper right")

    # Set aspect ratio (2:1)
    #ax1.set_aspect(aspect=0.5, adjustable='datalim')
    fig.set_size_inches(10,5)
    
    # Title and show
    plt.title("Stock Prices and Volume")
    plt.tight_layout()  # Adjust layout
    # Check if users is using kitty-terminal
    # if kitty then save image and display in term
    # if not, just show()
    #Fix this later(I mean the path and stuff)
    plt.savefig(temppath, format="png", dpi=300)
    if not "KITTY_WINDOW_ID" in os.environ:#.get("TERM", "").lower():
        plt.show()
    return None

# =========================
# Main Function
# =========================
def main():
    """
    Main function to run the script.
    """
    logger.info("Starting the script...")
    logger.info("Ending the script...")

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

