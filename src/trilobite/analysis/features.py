import numpy as np
from pandas import DataFrame

def prices_to_log_returns(adjclose_wide: DataFrame) -> DataFrame:
    """
    Normalises prices
    """
    return np.log(adjclose_wide / adjclose_wide.shift(1)).dropna()

