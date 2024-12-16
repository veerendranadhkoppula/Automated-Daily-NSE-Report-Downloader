import os
import shutil
import logging
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="file_organizer.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'  # Example for Gmail; adjust as needed
SMTP_PORT = 587
EMAIL_ADDRESS = 'veerendrakoppula68@gmail.com'  # Your email address
EMAIL_PASSWORD = 'yqzy pesz ufzu inpx'        # Your email password
RECIPIENT_EMAIL = 'veerendrakoppula68@gmail.com'  # Where to send alerts

# Function to send an email alert
def send_email(subject, events, completion_status, failures=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject

        # Build body content with events, completion status, and failure details
        body_content = f"Status: {completion_status}\n\nMajor Events:\n"
        for event in events:
            body_content += f"- {event}\n"

        if failures:
            body_content += "\nFailures:\n"
            for failure in failures:
                body_content += f"- {failure}\n"

        msg.attach(MIMEText(body_content, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

# Function to move a file into date and type-specific folders
def move_file_to_date_and_type_folder(src_path, date_dir, type_subfolder, events, failures):
    try:
        type_folder = os.path.join(date_dir, type_subfolder)
        os.makedirs(type_folder, exist_ok=True)

        filename = os.path.basename(src_path)
        dest_path = os.path.join(type_folder, filename)

        if os.path.exists(dest_path):
            logging.warning(f"Duplicate file found and deleted: {src_path}")
            os.remove(src_path)
            events.append(f"Deleted duplicate file: {filename}")
            return

        shutil.move(src_path, dest_path)
        logging.info(f"Moved file from {src_path} to {dest_path}")
        events.append(f"Moved {filename} to {type_subfolder} folder")

    except Exception as e:
        logging.error(f"Error moving file {src_path}: {str(e)}")
        failures.append(f"Error moving file {filename}: {str(e)}")

# Function to extract zip files and organize extracted files
def extract_and_organize_zip_file(zip_path, date_dir, events, failures):
    extract_path = os.path.join(date_dir, "EXTRACTED")
    os.makedirs(extract_path, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        logging.info(f"Extracted {zip_path} to {extract_path}")
        os.remove(zip_path)  # Optionally delete the zip file after extraction
        events.append(f"Extracted and organized contents of {zip_path}")

        # Organize extracted files within the date folder
        organize_files_in_directory(extract_path, date_dir, events, failures)

    except zipfile.BadZipFile:
        error_msg = f"Failed to extract {zip_path}: Bad zip file"
        logging.error(error_msg)
        failures.append(error_msg)
        send_email("Extraction Error", events, "Error", [error_msg])

# Function to organize files into date and type folders
def organize_files_in_directory(directory, date_dir, events, failures):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            extension = filename.lower().strip()
            if extension.endswith('.csv'):
                move_file_to_date_and_type_folder(file_path, date_dir, 'CSV', events, failures)
            elif extension.endswith('.dat'):
                move_file_to_date_and_type_folder(file_path, date_dir, 'DAT', events, failures)
            else:
                move_file_to_date_and_type_folder(file_path, date_dir, 'OTHERS', events, failures)

# Directories
source_dir = 'downloads'
base_dir = 'organized_downloads'
os.makedirs(base_dir, exist_ok=True)

# Today's date folder
today_date = datetime.now().strftime('%Y-%m-%d')
date_dir = os.path.join(base_dir, today_date)
os.makedirs(date_dir, exist_ok=True)

# Main processing
events = []
failures = []

try:
    events.append("Started processing files")

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        if os.path.isfile(file_path):
            if filename.lower().endswith('.zip'):
                # Extract and organize zip files
                extract_and_organize_zip_file(file_path, date_dir, events, failures)

            elif filename.lower().endswith('.csv'):
                move_file_to_date_and_type_folder(file_path, date_dir, 'CSV', events, failures)
            elif filename.lower().endswith('.dat'):
                move_file_to_date_and_type_folder(file_path, date_dir, 'DAT', events, failures)
            else:
                move_file_to_date_and_type_folder(file_path, date_dir, 'OTHERS', events, failures)

    completion_status = "Completed successfully" if not failures else "Completed with errors"
    events.append("File organization completed")
    send_email("File Organization Complete", events, completion_status, failures)

except Exception as e:
    error_msg = f"Unexpected error: {str(e)}"
    logging.error(error_msg)
    failures.append(error_msg)
    send_email("File Organizer Error", events, "Error",[error_msg])