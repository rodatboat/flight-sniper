"""Flight Parser - Parse flight data from Skyscanner HTML."""
import json
import logging
from pathlib import Path
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
    
    def _load_soup(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return BeautifulSoup(f.read(), 'html.parser')
    
    def _save_json(self, data, file_path):
        """Save parsed data to a JSON file with the same name.
        
        Args:
            data (dict): Parsed flight data to save
            file_path (str): Original HTML file path
        """
        try:
            json_path = Path(file_path).with_suffix('.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved JSON to {json_path}")
        except Exception as e:
            logger.error(f"Error saving JSON: {e}", exc_info=True)

    def parse_from_file(self, file_path):
        """Parse daily flight list from an HTML file (output/YYYY/MM/DD/...) and save as JSON."""
        logger.info(f"Reading HTML from file: {file_path}")
        try:
            data = self._read_flight_list_data(self._load_soup(file_path))
            self._save_json(data, file_path)
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"Error reading from file: {e}", exc_info=True)
            return {}

    def parse_monthly_from_file(self, file_path):
        """Parse monthly calendar view from an HTML file (output/YYYY/MM/...) and save as JSON."""
        logger.info(f"Reading monthly HTML from file: {file_path}")
        try:
            # Extract month from file path: output/YYYY/MM/filename.html
            path_parts = Path(file_path).parts
            month = None
            if len(path_parts) >= 2:
                try:
                    month = int(path_parts[-2])  # MM directory
                except (ValueError, IndexError):
                    pass
            
            data = self._read_calendar_data(self._load_soup(file_path), month=month)
            self._save_json(data, file_path)
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"Error reading monthly from file: {e}", exc_info=True)
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
        
    def parse_monthly_from_soup(self, soup, month=None):
        """Parse monthly calendar data from BeautifulSoup content.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object from the sniper run
            month (int): Optional month number (1-12) to include in results
            
        Returns:
            dict: Parsed monthly calendar data
        """
        logger.info("Parsing monthly calendar data from soup content")
        try:
            return self._read_calendar_data(soup, month=month)
        except Exception as e:
            logger.error(f"Error parsing monthly from soup: {e}", exc_info=True)
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
            'total_flights': 0
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
    
    def _read_calendar_data(self, soup, month=None):
        logger.info("Extracting calendar data...")
        calendar_data = {
            'dates': []
        }
        if month is not None:
            calendar_data['month'] = month

        try:
            grid = soup.find('div', class_=lambda x: x and 'BpkCalendarGrid_bpk-calendar-grid_' in x)
            if not grid:
                logger.warning("Calendar grid not found")
                return calendar_data

            rowgroup = grid.find('div', role='rowgroup')
            if not rowgroup:
                logger.warning("Calendar rowgroup not found")
                return calendar_data

            cells = rowgroup.find_all('div', role='gridcell')
            logger.info(f"Found {len(cells)} calendar cells")

            for cell in cells:
                button = cell.find('button')
                if not button:
                    continue

                day_p = button.find('p', class_=lambda x: x and 'date' in x.split())
                price_p = button.find('p', class_=lambda x: x and 'price' in x.split())

                day = day_p.get_text(strip=True) if day_p else None
                price = price_p.get_text(strip=True) if price_p else None
                # full date string e.g. "Friday, September 4, 2026, $121"
                aria_label = button.get('aria-label', '')

                if day or aria_label:
                    entry = {'day': day, 'price': price, 'aria_label': aria_label}
                    if month is not None:
                        entry['month'] = month
                    calendar_data['dates'].append(entry)
                    logger.debug(f"Calendar cell: {aria_label}")

            logger.info(f"Successfully extracted {len(calendar_data['dates'])} calendar dates")

        except Exception as e:
            logger.error(f"Error extracting calendar data: {e}", exc_info=True)

        return calendar_data
