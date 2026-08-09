from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://your-site.com")
    
    # driver.find_element("id", "username").send_keys("user")
    # driver.find_element("id", "password").send_keys("password")
    # driver.find_element("css selector", "button[type=submit]").click()

    print(driver.title)
    print(driver.page_source)

finally:
    driver.quit()