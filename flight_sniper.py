"""Flight Sniper - Scrape flight data from Skyscanner using SeleniumBase.
Runs on a schedule using APScheduler.
"""
import os
import time
import logging
from datetime import datetime, date
from urllib.parse import urlencode
from apscheduler.schedulers.background import BackgroundScheduler
from seleniumbase import sb_cdp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCHEDULE_HOURS = int(os.getenv('FLIGHT_SNIPER_SCHEDULE_HOURS', '1'))
OUTPUT_DIR = os.getenv('FLIGHT_SNIPER_OUTPUT_DIR', '/output')

BASE_URL = "https://www.skyscanner.com/transport/flights"

# Layover airport exclusions keyed by (from, to) in lowercase
ROUTE_LAYOVER_EXCLUSIONS = {
    ("dfwa", "wasa"): "!95673800,!95673643,!95673980,!95674227,!95673672,!95673391,!95673392,!95673906,!95673782,!95673705,!95673555,!104120241,!95674300,!95673753,!95674066,!95673412,!95673411,!95674097,!95673600,!95673788,!95673969,!95673821,!95673838,!128667334,!95673724,!95673750,!95565058,!95565057,!95673722,!95674009,!95673618,!95673938,!95673494,!95673694,!95673876",
    ("wasa", "dfwa"): "!95673800,!95673643,!95673980,!95673679,!95674227,!95673672,!95673391,!95673392,!95673906,!95673782,!95673621,!95673555,!104120241,!95674300,!95673753,!95673412,!95673411,!95673788,!95674077,!95674054,!95673821,!95673838,!128667334,!95673724,!95673750,!95565058,!95565057,!95673722,!95674009,!95673879,!95673618,!95673720,!95673938,!95673473,!95673694,!95673876,!95673870",
    ("dfwa", "miaa"): "!95673800,!95673643,!95673663,!95673672,!95673391,!95673392,!95673782,!95673705,!95673555,!95673412,!95673411,!95673600,!95673724,!95673750,!95565059,!95674009,!128667200,!95673446,!95673938,!95673694,!95673876,!95673870,!95673665",
    ("miaa", "dfwa"): "!95673800,!95673643,!95673663,!95673980,!95673672,!95673391,!95673392,!95673782,!95673705,!95673555,!95673412,!95673411,!95673600,!95673724,!95673750,!95565059,!95674009,!95673720,!95673938,!95673494,!95673694,!95673876,!95674105,!95673870,!95673665",
}

COMMON_PARAMS = {
    "adultsv2": "1",
    "cabinclass": "economy",
    "childrenv2": "",
    "rtn": "0",
    "outboundaltsenabled": "false",
    "inboundaltsenabled": "false",
    "preferdirects": "true",
}


def build_daily_url(from_airport: str, to_airport: str, flight_date: date) -> str:
    params = {**COMMON_PARAMS, "ref": "home", "duration": "360", "layover-duration": "0-0"}
    exclusions = ROUTE_LAYOVER_EXCLUSIONS.get((from_airport.lower(), to_airport.lower()))
    if exclusions:
        params["layover-airports"] = exclusions
    date_str = flight_date.strftime("%y%m%d")
    return f"{BASE_URL}/{from_airport}/{to_airport}/{date_str}/?{urlencode(params)}"


def build_monthly_url(from_airport: str, to_airport: str, year: int, month: int) -> str:
    oym = f"{str(year)[2:]}{month:02d}"
    params = {**COMMON_PARAMS, "iym": "", "oym": oym, "selectedoday": "01"}
    return f"{BASE_URL}/{from_airport}/{to_airport}?{urlencode(params)}"


def scrape_skyscanner(url: str) -> str:
    """Navigate to a Skyscanner URL and return beautified HTML."""
    logger.info(f"Scraping: {url}")
    sb = sb_cdp.Chrome(locale="en", undetectable=True)
    try:
        sb.goto(url)
        sb.sleep(2)

        logger.info("Checking for CAPTCHA...")
        sb.solve_captcha()
        sb.sleep(2)

        title = sb.get_title()
        logger.info(f"Page Title: {title}")
        logger.info(f"Page URL: {sb.get_current_url()}")

        soup = sb.get_beautiful_soup()
        logger.info(f"Page Content Length: {len(str(soup))}")

        if "You need to enable JavaScript" in str(soup) or "captcha" in str(soup).lower():
            logger.warning("⚠ Still seeing CAPTCHA or JS message")
        else:
            logger.info("✓ Successfully loaded Skyscanner!")

        return soup.prettify()
    finally:
        sb.quit()


def _save(html: str, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"✓ Saved to {output_path} ({len(html)} bytes)")


def scrape_daily(from_airport: str, to_airport: str, flight_date: date) -> None:
    """Scrape the daily flight list for a route and date."""
    url = build_daily_url(from_airport, to_airport, flight_date)
    html = scrape_skyscanner(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(
        OUTPUT_DIR,
        str(flight_date.year),
        f"{flight_date.month:02d}",
        f"{flight_date.day:02d}",
        f"{from_airport}_{to_airport}_{timestamp}.html",
    )
    _save(html, output_path)


def scrape_monthly(from_airport: str, to_airport: str, year: int, month: int) -> None:
    """Scrape the monthly calendar view for a route."""
    url = build_monthly_url(from_airport, to_airport, year, month)
    html = scrape_skyscanner(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(
        OUTPUT_DIR,
        str(year),
        f"{month:02d}",
        f"{from_airport}_{to_airport}_{timestamp}.html",
    )
    _save(html, output_path)


if __name__ == "__main__":
    logger.info("-"*40)
    logger.info(f"Flight Sniper - Starting")
    logger.info("-"*40)

    scrape_daily("dfwa", "wasa", date(2026, 9, 3))
    scrape_monthly("dfwa", "wasa", 2026, 9)

    # scheduler = BackgroundScheduler()
    # scheduler.add_job(
    #     lambda: scrape_daily("dfwa", "wasa", date(2026, 9, 3)),
    #     'interval',
    #     hours=SCHEDULE_HOURS,
    # )
    # scheduler.start()
    # logger.info(f"Scheduler started - will run every {SCHEDULE_HOURS} hour(s)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        # scheduler.shutdown()
        logger.info("Goodbye!")