import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

# Define download directory
download_dir = "downloads"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Set preferences for automatic download handling
prefs = {
    "download.default_directory": os.path.abspath(download_dir),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Path to your ChromeDriver (use double backslashes or raw string)
service = Service(r"C:\Users\veerendranadh koppul\Downloads\chromedriver-win64\chromedriver.exe") 
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open the NSE reports page
    driver.get("https://www.nseindia.com/all-reports")
    time.sleep(5)  # Give the page time to load

    # Find the div that contains the report download links
    report_div = driver.find_element(By.XPATH, "//div[@id='cr_equity_daily_Current']")

    # Find all report download links within that div
    report_divs = report_div.find_elements(By.XPATH, ".//div[contains(@class, 'reportsDownload')]")

    # Loop through all the reports and download them
    for report in report_divs:
        data_link = report.get_attribute("data-link")
        if data_link:
            print(f"Downloading from: {data_link}")
            driver.get(data_link)
            time.sleep(10)  # Allow enough time for each download

finally:
    # Quit the browser after downloads are complete
    driver.quit()
