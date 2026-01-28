import numpy as np
from pandas import DataFrame

def prices_to_log_returns(adjclose_wide: DataFrame) -> DataFrame:
    """
    Returns logs
    """
    px = adjclose_wide.where(adjclose_wide > 0.0)

    rets = np.log(px / px.shift(1))
    
    rets = rets.replace([np.inf, -np.inf], np.nan).dropna(axis=0, how="any")
    #return np.log(adjclose_wide / adjclose_wide.shift(1)).dropna()
    return rets

