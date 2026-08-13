"""Test Flight Parser - Test parser functionality without running the scraper."""
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from html_parser import FlightParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


SAMPLE_HTML_DIR = Path(__file__).parent / "sample_html"


def _log_flights(flights_data):
    logger.info("-"*40)
    logger.info("PARSING RESULTS")
    logger.info("-"*40)
    logger.info(f"Total flights found: {flights_data.get('total_flights', 0)}")
    if flights_data.get('flights'):
        for idx, flight in enumerate(flights_data['flights'], 1):
            logger.info("-"*40)
            logger.info(f"Flight {idx}:")
            for key, value in flight.items():
                logger.info(f"{key}: {value}")
    else:
        logger.warning("No flights found in the HTML")


def test_parse_from_file():
    """Test parsing a daily flight list from sample_html/day.html."""
    logger.info("-"*40)
    logger.info("Testing FlightParser.parse_from_file()")
    logger.info("-"*40)

    html_file = SAMPLE_HTML_DIR / "day.html"
    logger.info(f"Using HTML file: {html_file}")
    logger.info(f"File size: {html_file.stat().st_size} bytes")

    parser = FlightParser()
    flights_data = parser.parse_from_file(str(html_file))
    _log_flights(flights_data)
    return flights_data


def test_parse_monthly_from_file():
    """Test parsing a monthly calendar view from sample_html/month.html."""
    logger.info("-"*40)
    logger.info("Testing FlightParser.parse_monthly_from_file()")
    logger.info("-"*40)

    html_file = SAMPLE_HTML_DIR / "month.html"
    logger.info(f"Using HTML file: {html_file}")
    logger.info(f"File size: {html_file.stat().st_size} bytes")

    parser = FlightParser()
    calendar_data = parser.parse_monthly_from_file(str(html_file))

    logger.info("-"*40)
    logger.info("PARSING RESULTS")
    logger.info("-"*40)
    logger.info(f"Total calendar dates found: {len(calendar_data.get('dates', []))}")
    for entry in calendar_data.get('dates', []):
        logger.info(f"  {entry.get('date')} - {entry.get('price')}")

    return calendar_data


if __name__ == "__main__":
    logger.info("Starting Flight Parser Tests...\n")
    
    flights_result = test_parse_from_file()
    calendar_result = test_parse_monthly_from_file()
    
    logger.info("-"*40)
    logger.info("Tests Completed!")
    logger.info("-"*40)
