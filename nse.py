import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

# Import functions from main2
from main2 import organize_downloaded_files, create_today_date_folder
from Email import move_file_to_date_and_type_folder, extract_and_organize_zip_file  # Import functions from Email


chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent = your user agent")

# Set up download directory
download_dir = "C:\\Users\\veerendranadh koppul\\OneDrive\\Desktop\\Nse_Report_Downloader\\downloads"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

prefs = {
    "download.default_directory": os.path.abspath(download_dir),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Updated service path
service = Service(r"C:\Users\veerendranadh koppul\Downloads\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

def log_event(message):
    """Log messages for tracking."""
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def is_download_complete(file_name):
    """Check if the download is complete by verifying if a temporary file exists."""
    file_path = os.path.join(download_dir, file_name)
    return os.path.exists(file_path) and not file_path.endswith(".crdownload")

def download_report(data_link, file_name):
    """Attempt to download the report until the file is fully downloaded."""
    retry_count = 0
    while retry_count < 3:  # Retry up to 3 times if incomplete
        try:
            driver.get(data_link)
            log_event(f"Accessing download link: {data_link}")
            time.sleep(5)  # Wait for the download to start

            # Check if download is complete
            if is_download_complete(file_name):
                log_event(f"Download completed: {file_name}")
                # Organize files after each successful download
              #  organize_downloaded_files()
                break
            else:
                log_event(f"Incomplete download detected for {file_name}. Retrying ({retry_count + 1}/3)...")
                retry_count += 1
                time.sleep(2)  # Wait a bit before retrying
        except WebDriverException as e:
            log_event(f"Failed to download from {data_link}: {e}")
            retry_count += 1

try:
    driver.get("https://www.nseindia.com/all-reports")
    time.sleep(5)

    try:
        report_div = driver.find_element(By.XPATH, "//div[@id='cr_equity_daily_Current']")
    except Exception as e:
        log_event("Report not found on the page: " + str(e))
        driver.quit()
        exit()

    report_divs = report_div.find_elements(By.XPATH, ".//div[contains(@class, 'reportsDownload')]")
    if not report_divs:
        log_event("No reports available for download.")
        driver.quit()
        exit()

    for report in report_divs:
        try:
            data_link = report.get_attribute("data-link")
            if not data_link:
                log_event("Data link attribute missing or empty for a report.")
                continue

            file_name = data_link.split("/")[-1]  # Get the file name from the URL
            log_event(f"Downloading from: {data_link}")
            download_report(data_link, file_name)

        except Exception as e:
            log_event("Error processing report: " + str(e))

finally:
    driver.quit()
    # After all downloads are completed, create a dated folder and move files
   # create_today_date_folder()
