#Helper functions
import random

def stagger_requests(mintime: float = 0.2, maxtime: float = 0.9) -> float:
    """
    Creats a float in the range between the two numbers. 
    """
    if mintime >= maxtime:
        mintime, maxtime = maxtime, mintime
    return random.uniform(mintime, maxtime)
