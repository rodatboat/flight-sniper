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


def test_parse_from_file():
    """Test parsing flight data from the saved HTML file."""
    logger.info("-"*40)
    logger.info("Testing FlightParser.parse_from_file()")
    logger.info("-"*40)
    
    # Use the most recent HTML file in output directory
    output_dir = Path(__file__).parent / "output"
    
    if not output_dir.exists():
        logger.error(f"Output directory not found: {output_dir}")
        return
    
    # Find all HTML files and get the most recent one
    html_files = sorted(output_dir.glob("skyscanner_*.html"), reverse=True)
    
    if not html_files:
        logger.error("No HTML files found in output directory")
        return
    
    html_file = html_files[0]
    logger.info(f"Using HTML file: {html_file}")
    logger.info(f"File size: {html_file.stat().st_size} bytes")
    
    # Parse the file
    parser = FlightParser()
    flights_data = parser.parse_from_file(str(html_file))
    
    # Display results
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
    
    return flights_data


def test_parse_calendar():
    """Test parsing calendar data from the saved HTML file."""
    logger.info("-"*40)
    logger.info("Testing FlightParser.read_calendar_data()")
    logger.info("-"*40)
    
    from bs4 import BeautifulSoup
    
    output_dir = Path(__file__).parent / "output"
    html_files = sorted(output_dir.glob("skyscanner_*.html"), reverse=True)
    
    if not html_files:
        logger.error("No HTML files found in output directory")
        return
    
    html_file = html_files[0]
    
    # Read and parse
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    parser = FlightParser()
    calendar_data = parser.read_calendar_data(soup)
    
    # Display results
    logger.info("-"*40)
    logger.info("CALENDAR PARSING RESULTS")
    logger.info("-"*40)
    logger.info(f"Total calendar dates found: {len(calendar_data.get('dates', []))}")
    
    if calendar_data.get('dates'):
        logger.info("\nCalendar Details:")
        for idx, date_info in enumerate(calendar_data['dates'], 1):
            logger.info(f"  {idx}. {date_info}")
    else:
        logger.warning("No calendar dates found in the HTML")
    
    return calendar_data


if __name__ == "__main__":
    logger.info("Starting Flight Parser Tests...\n")
    
    # Test file parsing
    flights_result = test_parse_from_file()
    
    # Test calendar parsing
    # calendar_result = test_parse_calendar()
    
    logger.info("-"*40)
    logger.info("Tests Completed!")
    logger.info("-"*40)
