"""Utility functions for Flight Sniper."""
import os
import logging
from datetime import date
from pathlib import Path
import airportsdata

logger = logging.getLogger(__name__)

airports = airportsdata.load("IATA")
OUTPUT_DIR = os.getenv('FLIGHT_SNIPER_OUTPUT_DIR', './output')


def validate_iata(code: str) -> bool:
    """Return True if code is a known IATA airport code."""
    return code.upper() in airports


def expand_airport_code(code: str) -> str:
    """
    Extract valid airport code from user input.
    
    The 'A' suffix is a user-facing feature (e.g., DFWA) to indicate
    searching surrounding airports, but it's not a real IATA code.
    This function extracts just the valid 3-letter IATA code.
    
    Examples:
        'dfw' -> 'DFW'
        'dfwa' -> 'DFW'
    
    Args:
        code: Airport code (3-4 chars, optionally ending with 'A')
    
    Returns:
        The 3-letter IATA code in uppercase
    
    Raises:
        ValueError: If code is invalid format
    """
    code_upper = code.upper().strip()
    
    if len(code_upper) < 3 or len(code_upper) > 4:
        raise ValueError(f"Airport code must be 3-4 characters: {code}")
    
    # Extract first 3 characters (the actual IATA code)
    iata_code = code_upper[:3]
    
    # If there's a 4th character, it must be 'A'
    if len(code_upper) == 4 and code_upper[3] != 'A':
        raise ValueError(f"4th character must be 'A' (for surrounding airports): {code}")
    
    return iata_code


def validate_airports(from_code: str, to_code: str) -> bool:
    """
    Validate airport codes (extracting IATA from codes with optional 'A' suffix).
    
    Args:
        from_code: Departure airport code (3-4 chars, may end with 'A')
        to_code: Arrival airport code (3-4 chars, may end with 'A')
    
    Returns:
        True if both codes are valid, False otherwise
    """
    try:
        from_iata = expand_airport_code(from_code)
        to_iata = expand_airport_code(to_code)
        
        if not validate_iata(from_iata):
            logger.error(f"Invalid IATA code: {from_iata}")
            return False
        
        if not validate_iata(to_iata):
            logger.error(f"Invalid IATA code: {to_iata}")
            return False
        
        return True
    except ValueError as e:
        logger.error(str(e))
        return False


def find_latest_html(from_airport: str, to_airport: str, flight_date: date = None) -> str | None:
    """
    Find the latest HTML file for a given route and date.
    
    Args:
        from_airport: Departure airport code
        to_airport: Arrival airport code
        flight_date: Date to look for (defaults to today)
    
    Returns:
        Path to the latest HTML file, or None if not found
    """
    if flight_date is None:
        flight_date = date.today()
    
    date_dir = Path(OUTPUT_DIR) / str(flight_date.year) / f"{flight_date.month:02d}" / f"{flight_date.day:02d}"
    
    if not date_dir.exists():
        logger.warning(f"No directory found for {flight_date}: {date_dir}")
        return None
    
    # Find all matching HTML files
    pattern = f"{from_airport}_{to_airport}_*.html"
    html_files = sorted(date_dir.glob(pattern), reverse=True)
    
    if html_files:
        return str(html_files[0])
    
    logger.warning(f"No HTML files found matching pattern: {pattern}")
    return None


def find_latest_monthly_html(from_airport: str, to_airport: str, year: int, month: int) -> str | None:
    """
    Find the latest HTML file for a given route and month.
    
    Args:
        from_airport: Departure airport code
        to_airport: Arrival airport code
        year: Year to look for
        month: Month to look for
    
    Returns:
        Path to the latest HTML file, or None if not found
    """
    month_dir = Path(OUTPUT_DIR) / str(year) / f"{month:02d}"
    
    if not month_dir.exists():
        logger.warning(f"No directory found: {month_dir}")
        return None
    
    pattern = f"{from_airport}_{to_airport}_*.html"
    html_files = sorted(month_dir.glob(pattern), reverse=True)
    
    if html_files:
        return str(html_files[0])
    
    logger.warning(f"No HTML files found matching pattern: {pattern}")
    return None
