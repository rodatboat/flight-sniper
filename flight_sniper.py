"""Flight Sniper - Scrape flight data from Skyscanner using SeleniumBase.
Runs on a schedule using APScheduler.
"""
import os
import time
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from seleniumbase import sb_cdp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get schedule interval from environment variable (default: 1 hour)
SCHEDULE_HOURS = int(os.getenv('FLIGHT_SNIPER_SCHEDULE_HOURS', '1'))


def scrape_skyscanner():
    """Scrape flight data from Skyscanner."""
    logger.info("Starting Skyscanner scrape...")
    
    sb = sb_cdp.Chrome(locale="en", undetectable=True)
    
    try:
        url = "https://www.skyscanner.com/transport/flights/dfwa/wasa/260903/260908/?adultsv2=1&childrenv2=&cabinclass=economy&rtn=1&preferdirects=true&outboundaltsenabled=false&inboundaltsenabled=false&duration=360&layover-airports=%2195673800%2C%2195673643%2C%2195673980%2C%2195673672%2C%2195673391%2C%2195673392%2C%2195673906%2C%2195673782%2C%2195673705%2C%2195673555%2C%21104120241%2C%2195673412%2C%2195673411%2C%2195674097%2C%2195673608%2C%2195673788%2C%2195673969%2C%2195673651%2C%2195673821%2C%2195673838%2C%21128667334%2C%2195673724%2C%2195673750%2C%2195565058%2C%2195565057%2C%2195565059%2C%2195673722%2C%2195674009%2C%2195673879%2C%2195673618%2C%2195673938%2C%2195674062%2C%2195673494%2C%2195673876%2C%2195673870&layover-duration=0-0"
        
        logger.info("Navigating to Skyscanner...")
        sb.goto(url)
        sb.sleep(2)
        
        # Solve CAPTCHA if present
        logger.info("Checking for CAPTCHA...")
        sb.solve_captcha()
        sb.sleep(2)
        
        # Print page information
        title = sb.get_title()
        current_url = sb.get_current_url()
        logger.info(f"Page Title: {title}")
        logger.info(f"Page URL: {current_url}")
        
        # Get page content for inspection
        soup = sb.get_beautiful_soup()
        logger.info(f"Page Content Length: {len(str(soup))}")
        
        # Check if we got past the CAPTCHA
        if "You need to enable JavaScript" in str(soup) or "captcha" in str(soup).lower():
            logger.warning("⚠ Still seeing CAPTCHA or JS message")
        else:
            logger.info("✓ Successfully loaded Skyscanner!")
        
        # Beautify and save to temp.html with timestamp
        beautified_html = soup.prettify()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/output/skyscanner_{timestamp}.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(beautified_html)
        logger.info(f"✓ Saved beautified HTML to {output_path} ({len(beautified_html)} bytes)")
        
        # Example: Extract flight information
        # flights = sb.find_elements("div[data-testid='flight-card']")
        # for flight in flights:
        #     logger.info(flight.text)
        
        logger.info("✓ Skyscanner scrape completed!")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
    finally:
        sb.quit()


if __name__ == "__main__":
    # Run immediately on start
    logger.info("="*50)
    logger.info(f"Flight Sniper - Starting scheduler (every {SCHEDULE_HOURS} hour(s))")
    logger.info("="*50)
    scrape_skyscanner()
    
    # Set up scheduler with configurable interval
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrape_skyscanner, 'interval', hours=SCHEDULE_HOURS)
    scheduler.start()
    logger.info(f"Scheduler started - will run every {SCHEDULE_HOURS} hour(s)")
    
    # Keep the application running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Goodbye!")