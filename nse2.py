import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up directories
source_dir = 'C:\\Users\\veerendranadh koppul\\OneDrive\\Desktop\\Nse_Report_Downloader\\downloads'
csv_dir = os.path.join(source_dir, 'CSV')
dat_dir = os.path.join(source_dir, 'DAT')

# Create directories if they don't exist
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(dat_dir, exist_ok=True)

# URL to fetch the report
url = "https://www.nseindia.com/market-data/live-equity-market"

# Set up Selenium WebDriver (ensure you have the correct path to chromedriver)
service = Service("path/to/chromedriver")  # Update this path
driver = webdriver.Chrome(service=service)

try:
    driver.get(url)
    print("Page loaded successfully.")
    
    # Wait for the link to appear (adjust the text or class if needed)
    wait = WebDriverWait(driver, 10)
    csv_link_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.csv')]")))
    csv_link = csv_link_element.get_attribute('href')

    print(f"CSV link found: {csv_link}")
except Exception as e:
    print(f"Failed to find CSV link: {e}")
    driver.quit()
    exit(1)

driver.quit()

# Download the CSV file
today_date = datetime.now().strftime('%Y-%m-%d')
csv_file_path = os.path.join(csv_dir, f'nse_report_{today_date}.csv')

try:
    csv_response = requests.get(csv_link)
    csv_response.raise_for_status()
    with open(csv_file_path, 'wb') as file:
        file.write(csv_response.content)
    print(f"CSV file downloaded successfully: {csv_file_path}")
except requests.exceptions.RequestException as e:
    print(f"Failed to download CSV file: {e}")
    exit(1)

# Processing and saving data as .dat fil
