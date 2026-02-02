#Helper functions
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def stagger_requests(mintime: float = 0.1, maxtime: float = 0.3) -> float:
    """
    Creats a float in the range between the two numbers. 
    """
    if mintime >= maxtime:
        mintime, maxtime = maxtime, mintime
    return random.uniform(mintime, maxtime)

def period_to_date(period: str, *, end_date: date) -> Tuple[Optional[date], date]:
    """
    Converts a period like '12d', '12w', '12m', '12y' 'max' into start_date
    and end_date

    Params:
    - period, string
    - end_date, comes in as a python date(provided by caller)
    """
    p = period.strip().lower()
    if p in {"max", "all"}:
        return None, end_date
    
    m, p = p[-1:], p[:-1]
    try:
        p = int(p)
    except ValueError:
        logger.info(f"Cannot convert {p} to integer")


