"""Utility functions for Flight Sniper."""
import airportsdata

airports = airportsdata.load("IATA")

def validate_iata(code: str) -> bool:
    """Return True if code is a known IATA airport code."""
    return code.upper() in airports
    