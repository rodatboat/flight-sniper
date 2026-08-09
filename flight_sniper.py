from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    try:
        page.goto("https://www.skyscanner.com/transport/flights/dfwa/wasa/260903/260908/?adultsv2=1&childrenv2=&cabinclass=economy&rtn=1&preferdirects=true&outboundaltsenabled=false&inboundaltsenabled=false&duration=360&layover-airports=%2195673800%2C%2195673643%2C%2195673980%2C%2195673672%2C%2195673391%2C%2195673392%2C%2195673906%2C%2195673782%2C%2195673705%2C%2195673555%2C%21104120241%2C%2195673412%2C%2195673411%2C%2195674097%2C%2195673608%2C%2195673788%2C%2195673969%2C%2195673651%2C%2195673821%2C%2195673838%2C%21128667334%2C%2195673724%2C%2195673750%2C%2195565058%2C%2195565057%2C%2195565059%2C%2195673722%2C%2195674009%2C%2195673879%2C%2195673618%2C%2195673938%2C%2195674062%2C%2195673494%2C%2195673876%2C%2195673870&layover-duration=0-0")
        time.sleep(3)
        print(page.title())
        print(page.content())
    finally:
        browser.close()