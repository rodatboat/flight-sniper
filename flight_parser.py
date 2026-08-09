"""Flight Parser - Parse flight data from Skyscanner HTML."""
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class FlightParser:
    """Parser for extracting flight data from Skyscanner HTML."""
    
    def parse_from_file(self, file_path):
        """Parse flight data from an HTML file.
        
        Args:
            file_path (str): Path to the HTML file to parse
            
        Returns:
            dict: Parsed flight data
        """
        logger.info(f"Reading HTML from file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            return self._read_flight_list_data(soup)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"Error reading from file: {e}", exc_info=True)
            return {}
    
    def parse_from_soup(self, soup):
        """Parse flight data from BeautifulSoup content.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object from the sniper run
            
        Returns:
            dict: Parsed flight data
        """
        logger.info("Parsing flight data from soup content")
        try:
            return self._read_flight_list_data(soup)
        except Exception as e:
            logger.error(f"Error parsing from soup: {e}", exc_info=True)
            return {}
    
    def _read_flight_list_data(self, soup):
        """Read flight list data from soup content.
        
        This is the shared child method called by both parse methods.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object containing the page
            
        Returns:
            dict: Dictionary containing flight data
        """
        logger.info("Extracting flight list data...")
        flights_data = {
            'flights': [],
            'total_flights': 0,
            'parsing_timestamp': None
        }
        
        try:
            # Find flight cards - dummy implementation
            flight_cards = soup.find_all('div', {'data-testid': 'flight-card'})
            logger.info(f"Found {len(flight_cards)} flight cards")
            
            for idx, card in enumerate(flight_cards, 1):
                flight_info = {}
                
                # Dummy parsing: extract various div elements
                price_div = card.find('div', class_='price')
                if price_div:
                    flight_info['price'] = price_div.get_text(strip=True)
                
                airline_div = card.find('div', class_='airline')
                if airline_div:
                    flight_info['airline'] = airline_div.get_text(strip=True)
                
                duration_div = card.find('div', class_='duration')
                if duration_div:
                    flight_info['duration'] = duration_div.get_text(strip=True)
                
                stops_div = card.find('div', class_='stops')
                if stops_div:
                    flight_info['stops'] = stops_div.get_text(strip=True)
                
                if flight_info:
                    flights_data['flights'].append(flight_info)
                    logger.debug(f"Flight {idx}: {flight_info}")
            
            flights_data['total_flights'] = len(flights_data['flights'])
            logger.info(f"Successfully extracted {flights_data['total_flights']} flights")
            
        except Exception as e:
            logger.error(f"Error extracting flight list data: {e}", exc_info=True)
        
        return flights_data
    
    def read_calendar_data(self, soup):
        """Read calendar data from soup content (dummy method).
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object containing the page
            
        Returns:
            dict: Dictionary containing calendar data
        """
        logger.info("Extracting calendar data...")
        calendar_data = {
            'dates': [],
            'availability': {}
        }
        
        try:
            # Dummy implementation: find calendar divs
            calendar_divs = soup.find_all('div', class_='calendar-date')
            logger.info(f"Found {len(calendar_divs)} calendar dates")
            
            for date_div in calendar_divs:
                date_text = date_div.get_text(strip=True)
                price_div = date_div.find('div', class_='calendar-price')
                price = price_div.get_text(strip=True) if price_div else None
                
                calendar_data['dates'].append({
                    'date': date_text,
                    'price': price
                })
                logger.debug(f"Calendar date: {date_text} - {price}")
            
            logger.info(f"Successfully extracted {len(calendar_data['dates'])} calendar dates")
            
        except Exception as e:
            logger.error(f"Error extracting calendar data: {e}", exc_info=True)
        
        return calendar_data
