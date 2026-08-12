"""Flight Parser - Parse flight data from Skyscanner HTML."""
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class FlightParser:
    """Parser for extracting flight data from Skyscanner HTML."""
    
    def _safe_get_text(self, element, selector=None):
        """Safely extract text from an element or find it first."""
        if not element:
            return None
        if selector:
            element = element.find(selector)
        if element:
            return element.get_text(strip=True)
        return None
    
    def _parse_time_location(self, leg_div):
        """Parse departure/arrival div with nested span > div > span structure."""
        time_val = None
        location_val = None
        
        spans = leg_div.find_all('span', recursive=False)
        if len(spans) >= 2:
            # First span: time (span > div > span)
            time_val = self._safe_get_text(spans[0].find('div'), 'span')
            # Second span: location (span > div > span)
            location_val = self._safe_get_text(spans[1].find('div'), 'span')
        
        return time_val, location_val
    
    def _parse_leg_info(self, leg_info_divs, prefix=''):
        """Parse leg info with 3 divs: departure, duration/stops, arrival."""
        leg_data = {}
        
        if len(leg_info_divs) >= 3:
            # Index 0: departure
            dep_time, dep_airport = self._parse_time_location(leg_info_divs[0])
            if dep_time:
                leg_data[f'{prefix}departure_time'] = dep_time
            if dep_airport:
                leg_data[f'{prefix}departure_airport'] = dep_airport
            
            # Index 1: duration and stops
            duration = self._safe_get_text(leg_info_divs[1], 'span')
            if duration:
                leg_data[f'{prefix}flight_duration'] = duration
            stops_container = leg_info_divs[1].find('div', class_=lambda x: x and 'stopsLabelContainer' in x)
            stops = self._safe_get_text(stops_container, 'span')
            if stops:
                leg_data[f'{prefix}stops_info'] = stops
            
            # Index 2: arrival
            arr_time, arr_airport = self._parse_time_location(leg_info_divs[2])
            if arr_time:
                leg_data[f'{prefix}arrival_time'] = arr_time
            if arr_airport:
                leg_data[f'{prefix}arrival_airport'] = arr_airport
        
        return leg_data
    
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
            flight_cards = soup.find_all('div', class_=lambda x: x and 'FlightsTicket_container_' in x)
            logger.info(f"Found {len(flight_cards)} flight cards")
            
            for idx, card in enumerate(flight_cards, 1):
                flight_info = {}
                
                # Extract price
                price_div = card.find('div', class_=lambda x: x and 'TicketStubPrice_priceWrapper_' in x)
                if price_div:
                    flight_info['price'] = price_div.get_text(strip=True)
                
                # Extract airline
                airline_span = card.find('span', class_=lambda x: x and 'LogoImage_label__' in x)
                if airline_span:
                    airline_text = self._safe_get_text(airline_span, 'span')
                    if airline_text:
                        flight_info['airline'] = airline_text

                duration_div = card.find_all('div', class_=lambda x: x and 'LegDetails_containerTicket_' in x)
                
                # Parse outbound leg
                to_duration_div = duration_div[0] if duration_div else None
                if to_duration_div:
                    leg_info = to_duration_div.find('div', class_=lambda x: x and 'LegInfo_legInfo_' in x)
                    if leg_info:
                        leg_info_divs = leg_info.find_all('div', recursive=False)
                        flight_info.update(self._parse_leg_info(leg_info_divs))
                
                # Parse return leg
                from_duration_div = duration_div[1] if len(duration_div) > 1 else None
                if from_duration_div:
                    leg_info = from_duration_div.find('div', class_=lambda x: x and 'LegInfo_legInfo_' in x)
                    if leg_info:
                        leg_info_divs = leg_info.find_all('div', recursive=False)
                        flight_info.update(self._parse_leg_info(leg_info_divs, prefix='return_'))
                
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
