"""Flight Sniper CLI Runner - Scrape and parse flight data with CLI arguments."""
import os
import sys
import logging
import argparse
from datetime import datetime, date
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from flight_sniper import scrape_daily, scrape_monthly
from html_parser import FlightParser
from util import (
    validate_iata,
    expand_airport_code,
    validate_airports,
    find_latest_html,
    find_latest_monthly_html,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = os.getenv('FLIGHT_SNIPER_OUTPUT_DIR', './output')


def run_daily_scrape(from_airport: str, to_airport: str, flight_date: date) -> str | None:
    """
    Scrape daily flights and return path to HTML file.
    
    Args:
        from_airport: Departure airport code
        to_airport: Arrival airport code
        flight_date: Date to scrape
    
    Returns:
        Path to the saved HTML file
    """
    logger.info(f"Scraping daily flights: {from_airport} -> {to_airport} on {flight_date}")
    scrape_daily(from_airport, to_airport, flight_date)
    
    # Find and return the latest HTML file
    return find_latest_html(from_airport, to_airport, flight_date)


def run_monthly_scrape(from_airport: str, to_airport: str, year: int, month: int) -> str | None:
    """
    Scrape monthly calendar and return path to HTML file.
    
    Args:
        from_airport: Departure airport code
        to_airport: Arrival airport code
        year: Year to scrape
        month: Month to scrape
    
    Returns:
        Path to the saved HTML file
    """
    logger.info(f"Scraping monthly calendar: {from_airport} -> {to_airport} for {year}-{month:02d}")
    scrape_monthly(from_airport, to_airport, year, month)
    
    # Find and return the latest HTML file
    return find_latest_monthly_html(from_airport, to_airport, year, month)


def parse_and_display(html_path: str, is_monthly: bool = False) -> None:
    """
    Parse HTML file and display results.
    
    Args:
        html_path: Path to HTML file to parse
        is_monthly: Whether this is a monthly calendar view
    """
    if not html_path or not Path(html_path).exists():
        logger.error(f"HTML file not found: {html_path}")
        return
    
    logger.info(f"Parsing HTML: {html_path}")
    parser = FlightParser()
    
    if is_monthly:
        results = parser.parse_monthly_from_file(html_path)
        logger.info("-" * 40)
        logger.info("MONTHLY CALENDAR RESULTS")
        logger.info("-" * 40)
        logger.info(f"Total calendar dates found: {len(results.get('dates', []))}")
        for entry in results.get('dates', []):
            logger.info(f"  Day {int(entry.get('day') or 0):02d} - {entry.get('price', 'N/A'):>6}  ({entry.get('aria_label', 'N/A')})")
    else:
        results = parser.parse_from_file(html_path)
        logger.info("-" * 40)
        logger.info("DAILY FLIGHT RESULTS")
        logger.info("-" * 40)
        logger.info(f"Total flights found: {results.get('total_flights', 0)}")
        if results.get('flights'):
            for idx, flight in enumerate(results['flights'], 1):
                logger.info("-" * 40)
                logger.info(f"Flight {idx}:")
                for key, value in flight.items():
                    logger.info(f"  {key}: {value}")
        else:
            logger.warning("No flights found in the HTML")


def main():
    parser = argparse.ArgumentParser(
        description="Flight Sniper CLI - Scrape and parse Skyscanner flights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape daily one-way flights
  python cli_runner.py --daily --from DFW --to MIA --date 2026-09-03

  # Scrape monthly calendar with surrounding airports
  python cli_runner.py --monthly --from DFWA --to MIAA --year 2026 --month 9

  # Scrape and parse daily flights
  python cli_runner.py --daily --from DFW --to MIA --date 2026-09-03 --parse

  # Round-trip flights (reserved for future use)
  python cli_runner.py --daily --from DFW --to MIA --date 2026-09-03 --roundtrip
        """
    )
    
    # Scrape type
    scrape_group = parser.add_mutually_exclusive_group(required=True)
    scrape_group.add_argument('--daily', action='store_true', help='Scrape daily flight list')
    scrape_group.add_argument('--monthly', action='store_true', help='Scrape monthly calendar')
    
    # Route
    parser.add_argument('--from', dest='from_airport', required=True,
                       help='Departure IATA code (e.g., DFW, or DFWA to search surrounding airports)')
    parser.add_argument('--to', dest='to_airport', required=True,
                       help='Arrival IATA code (e.g., MIA, or MIAA to search surrounding airports)')
    
    # Date/Time
    parser.add_argument('--date', type=str, default=str(date.today()),
                       help='Flight date (YYYY-MM-DD, default: today)')
    parser.add_argument('--year', type=int, default=date.today().year,
                       help='Year for monthly scrape')
    parser.add_argument('--month', type=int, default=date.today().month,
                       help='Month for monthly scrape (1-12)')
    
    # Trip type
    parser.add_argument('--roundtrip', action='store_true',
                       help='Round-trip flights (one-way is default)')
    
    # Parsing
    parser.add_argument('--parse', action='store_true',
                       help='Parse and display results after scraping')
    
    args = parser.parse_args()
    
    logger.info("-" * 40)
    logger.info("Flight Sniper CLI Runner")
    logger.info("-" * 40)
    
    # Validate and extract airport codes
    if not validate_airports(args.from_airport, args.to_airport):
        logger.error("Airport validation failed!")
        return 1
    
    # Extract the valid IATA codes
    from_base = expand_airport_code(args.from_airport)
    to_base = expand_airport_code(args.to_airport)
    
    html_path = None
    
    try:
        if args.daily:
            flight_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            
            logger.info(f"Trip Type: {'Round-trip' if args.roundtrip else 'One-way'}")
            logger.info(f"Route: {from_base} -> {to_base}")
            logger.info(f"Date: {flight_date}")
            
            html_path = run_daily_scrape(from_base, to_base, flight_date)
        
        else:  # monthly
            if not 1 <= args.month <= 12:
                logger.error("Month must be between 1 and 12")
                return 1
            
            logger.info(f"Trip Type: {'Round-trip' if args.roundtrip else 'One-way'}")
            logger.info(f"Route: {from_base} -> {to_base}")
            logger.info(f"Period: {args.year}-{args.month:02d}")
            
            html_path = run_monthly_scrape(from_base, to_base, args.year, args.month)
        
        if html_path:
            logger.info(f"✓ Successfully scraped: {html_path}")
            
            if args.parse:
                parse_and_display(html_path, is_monthly=args.monthly)
        else:
            logger.error("Failed to scrape flights")
            return 1
    
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    logger.info("-" * 40)
    logger.info("Completed successfully!")
    logger.info("-" * 40)
    return 0


if __name__ == "__main__":
    sys.exit(main())
