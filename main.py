# Built-in libraries
import json  # Provides functions to work with JSON data (parsing, serializing, etc.)
import os  # Provides functions to interact with the operating system (file paths, directories, environment variables, etc.)
import urllib.parse  # Helps to parse and manipulate URLs (e.g., breaking a URL into components like scheme, host, path)
import re  # Regular expression module, used for advanced string pattern matching and text extraction
import time  # Provides time-related functions (e.g., sleep, time stamps)
import shutil  # Allows file operations like copying, moving, and deleting files and directories

# Selenium - for browser automation
from selenium import (
    webdriver,
)  # Main Selenium package to control a web browser via code
from selenium.webdriver.chrome.options import (
    Options,
)  # Allows customization of Chrome browser options (e.g., headless mode)
from selenium.webdriver.chrome.service import (
    Service,
)  # Manages the background service that runs ChromeDriver
from selenium.webdriver.chrome.webdriver import (
    WebDriver,
)  # Defines the WebDriver class specific to Chrome

# WebDriver Manager - handles automatic installation and setup of the correct ChromeDriver
from webdriver_manager.chrome import (
    ChromeDriverManager,
)  # Automatically downloads and manages the appropriate ChromeDriver version

# PDF handling library
import fitz  # PyMuPDF library; used for reading, writing, and editing PDF files

# External data validation
import validators  # Used to validate data like URLs, emails, etc. (e.g., check if a string is a valid URL)

# HTML parsing library
from bs4 import (
    BeautifulSoup,
)  # Used for parsing and navigating HTML and XML documents (web scraping)

# HTTP requests
import requests  # Allows sending HTTP requests (GET, POST, etc.) and handling responses


# Checks if a file exists at the given system path
def check_file_exists(system_path: str) -> bool:
    return os.path.isfile(path=system_path)  # Return True if file exists


# Removes duplicate items from a list
def remove_duplicates_from_slice(provided_slice: list[str]) -> list[str]:
    return list(
        set(provided_slice)
    )  # Convert to set to remove duplicates, then back to list


# Validate a given url
def validate_url(given_url: str) -> bool:
    return validators.url(given_url)


# Extracts and returns the cleaned filename from a URL
def url_to_filename(url: str) -> str:
    filename: str = urllib.parse.urlparse(url=url).path.split(sep="/")[-1].lower()
    # Remove special characters except for alphanumerics, dots, underscores, and dashes
    cleaned_filename: str = re.sub(pattern=r"[^a-z0-9._-]", repl="", string=filename)
    return cleaned_filename.lower()


# Uses Selenium to save the HTML content of a URL into a file
def save_html_with_selenium(url: str, output_file: str) -> None:
    options = Options()  # Create Chrome options object
    options.add_argument(argument="--headless=new")  # Run Chrome in new headless mode
    options.add_argument(
        argument="--disable-blink-features=AutomationControlled"
    )  # Avoid detection
    options.add_argument(argument="--window-size=1920,1080")  # Set browser window size
    options.add_argument(
        argument="--disable-gpu"
    )  # Disable GPU for headless compatibility
    options.add_argument(
        argument="--no-sandbox"
    )  # Disable sandbox (needed in some environments)
    options.add_argument(
        argument="--disable-dev-shm-usage"
    )  # Avoid shared memory issues
    options.add_argument(argument="--disable-extensions")  # Disable browser extensions
    options.add_argument(argument="--disable-infobars")  # Remove automation warning bar

    service = Service(
        executable_path=ChromeDriverManager().install()
    )  # Install ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)  # Launch browser

    try:
        driver.get(url=url)  # Open the given URL
        driver.refresh()  # Refresh the page
        html: str = driver.page_source  # Get page source HTML
        append_write_to_file(system_path=output_file, content=html)  # Save HTML to file
        print(f"Page {url} HTML content saved to {output_file}")  # Confirm success
    finally:
        driver.quit()  # Always quit the driver


# Appends content to a file
def append_write_to_file(system_path: str, content: str) -> None:
    with open(
        file=system_path, mode="a", encoding="utf-8"
    ) as file:  # Open in append mode
        file.write(content)  # Write the provided content


# Sets up Chrome driver with options for downloading files
def initialize_web_driver(download_folder: str) -> webdriver.Chrome:
    chrome_options = Options()  # Create Chrome options object
    chrome_options.add_experimental_option(  # Add download preferences
        name="prefs",
        value={
            "download.default_directory": download_folder,  # Set download directory
            "plugins.always_open_pdf_externally": True,  # Open PDFs externally
            "download.prompt_for_download": False,  # Do not prompt for download
        },
    )
    chrome_options.add_argument(argument="--headless")  # Run in headless mode
    return webdriver.Chrome(  # Return Chrome WebDriver with these options
        service=Service(executable_path=ChromeDriverManager().install()),
        options=chrome_options,
    )


# Waits for a new PDF file to appear in a directory
def wait_for_pdf_download(
    download_folder: str, files_before_download: set[str], timeout_seconds: int = 3
) -> str:
    deadline: float = time.time() + timeout_seconds  # Calculate timeout deadline
    while time.time() < deadline:  # While still within the timeout period
        current_files = set(
            os.listdir(path=download_folder)
        )  # Get current files in directory
        new_pdf_files: list[str] = [  # List new files that are PDFs
            f
            for f in (current_files - files_before_download)
            if f.lower().endswith(".pdf")
        ]
        if new_pdf_files:  # If a new PDF is found
            return os.path.join(
                download_folder, new_pdf_files[0]
            )  # Return its full path
    raise TimeoutError("PDF download timed out.")  # Raise error if no file appears


# Downloads a PDF from a given URL using Selenium
def download_single_pdf(url: str, filename: str, output_folder: str) -> None:
    os.makedirs(
        name=output_folder, exist_ok=True
    )  # Create the folder if it doesn't exist
    target_file_path: str = os.path.join(
        output_folder, filename
    )  # Final path for the PDF

    if check_file_exists(system_path=target_file_path):  # Skip if file already exists
        print(f"File already exists: {target_file_path}")
        return

    driver: WebDriver = initialize_web_driver(
        download_folder=output_folder
    )  # Launch headless browser
    try:
        print(f"Starting download from: {url}")  # Log start
        files_before = set(os.listdir(output_folder))  # Record files before download
        driver.get(url=url)  # Visit the URL

        downloaded_pdf_path: str = wait_for_pdf_download(
            download_folder=output_folder, files_before_download=files_before
        )  # Wait for file

        shutil.move(
            src=downloaded_pdf_path, dst=target_file_path
        )  # Move to target path
        print(f"Download complete: {target_file_path}")  # Confirm success

    except Exception as e:  # Catch and log any exception
        print(f"Error downloading PDF: {e}")
    finally:
        driver.quit()  # Close browser


# Deletes a file from the system
def remove_system_file(system_path: str) -> None:
    os.remove(path=system_path)  # Delete the file


# Recursively walk through a directory and find files with a specific extension
def walk_directory_and_extract_given_file_extension(
    system_path: str, extension: str
) -> list[str]:
    matched_files: list[str] = []  # List to store found files
    for root, _, files in os.walk(top=system_path):  # Walk through directories
        for file in files:  # Check each file
            if file.endswith(extension):  # Match the desired extension
                full_path: str = os.path.abspath(
                    path=os.path.join(root, file)
                )  # Get full path
                matched_files.append(full_path)  # Add to result list
    return matched_files  # Return all matched file paths


# Validates if a PDF file can be opened and has at least one page
def validate_pdf_file(file_path: str) -> bool:
    try:
        doc = fitz.open(file_path)  # Attempt to open PDF
        if doc.page_count == 0:  # Check if PDF has no pages
            print(f"'{file_path}' is corrupt or invalid: No pages")  # Log error
            return False  # Indicate invalid PDF
        return True  # PDF is valid
    except RuntimeError as e:  # Handle exception on open failure
        print(f"'{file_path}' is corrupt or invalid: {e}")  # Log error
        return False  # Indicate invalid PDF


# Extracts and returns the file name (with extension) from a path
def get_filename_and_extension(path: str) -> str:
    return os.path.basename(p=path)  # Get only file name from full path


# Checks if a string contains at least one uppercase letter
def check_upper_case_letter(content: str) -> bool:
    return any(char.isupper() for char in content)  # True if any character is uppercase


def extract_pdfnames_from_response(filename: str) -> list[str]:
    """
    Extracts the list of 'pdfname' values from a JSON file with a nested structure:

    Args:
        filename (str): The path to the JSON file.

    Returns:
        list[str]: A list containing all pdfname strings found inside 'items'.
                   Returns an empty list if none are found or on invalid structure.
    """

    # Open the JSON file in read mode with UTF-8 encoding
    with open(filename, "r", encoding="utf-8") as file:
        # Parse JSON content into a Python dictionary
        data = json.load(file)

    # Access the 'response' key safely; returns empty dict if missing
    response = data.get("response", {})

    # From 'response', get the 'items' list; default to empty list if missing
    items = response.get("items", [])

    # Check if 'items' is really a list (expected type)
    if not isinstance(items, list):
        print("Error: 'items' key is not a list.")
        return []

    # Iterate over each dictionary in 'items' list
    # Extract the value of 'pdfname' if it exists in that dictionary
    pdf_names: list[str] = [item.get("pdfname") for item in items if "pdfname" in item]

    # Return the list of pdfname strings
    return pdf_names


def fetch_fmc_data(output_file_base: str = "api_response") -> None:
    """
    Fetches data from two pages of the FMC SDS Viewer API and saves each page's result to a separate JSON file.

    Args:
        output_file_base (str): Base name for the output JSON files. Page number and .json extension will be added.
    """

    # Remove '.json' from base if included
    if output_file_base.lower().endswith(".json"):
        output_file_base = output_file_base[:-5]

    url = "https://apisdsviewer.fmc.com/api/ReportData/GetPagedData"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://sdsviewer.fmc.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://sdsviewer.fmc.com/",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    }

    for page_number in [1, 2]:
        payload = json.dumps(
            {
                "IsExportToExcel": False,
                "QuerySearchModel": {"RevisionDateFilter": {}, "PublishDateFilter": {}},
                "pageNumber": page_number,
                "pageSize": 5000,
            }
        )

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        json_data = response.json()

        # Write to a file named like: api_response_page_1.json
        output_filename = f"{output_file_base}_page_{page_number}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)

        print(f"Saved page {page_number} data to {output_filename}")


def main() -> None:
    output_base = "api_response"  # Base name for output JSON files
    json_files = [
        f"{output_base}_page_1.json",
        f"{output_base}_page_2.json",
    ]  # Expected paginated response files

    # Step 1: Clean up old JSON response files if they already exist
    for file_path in json_files:
        if check_file_exists(system_path=file_path):
            remove_system_file(
                system_path=file_path
            )  # Delete existing file to avoid stale data

    # Step 2: Fetch fresh data and save to separate JSON files
    fetch_fmc_data(output_file_base=output_base)

    # Step 3: Initialize an empty list to store all PDF links from both files
    all_pdf_links: list[str] = []

    # Step 4: Extract PDF links from each JSON file
    for file_path in json_files:
        if check_file_exists(system_path=file_path):
            links = extract_pdfnames_from_response(
                file_path
            )  # Extract links from response
            all_pdf_links.extend(links)  # Add to master list
        else:
            print(f"File {file_path} does not exist.")  # Handle missing file

    # Step 5: Remove duplicate PDF links
    pdf_links = remove_duplicates_from_slice(provided_slice=all_pdf_links)
    ammount_of_pdf = len(pdf_links)  # Total number of unique PDFs to process
    ammount_of_pdf_downloaded = 0  # Counter for successfully downloaded PDFs

    # Step 6: Download each PDF
    for pdf_link in pdf_links:
        # Ensure URL is fully qualified; prepend base if necessary
        if not validate_url(given_url=pdf_link):
            pdf_link = "https://sdsviewer.fmc.com/SDS_DOCS/" + pdf_link
            print(f"Invalid URL adjusted: {pdf_link}")

        filename = url_to_filename(url=pdf_link)  # Convert URL to a safe filename
        output_dir = os.path.abspath(
            path="PDFs"
        )  # Absolute path to the download directory

        # Log progress
        print(f"Remaining PDF links: {ammount_of_pdf - ammount_of_pdf_downloaded}")
        ammount_of_pdf_downloaded += 1
        print(f"Downloaded so far: {ammount_of_pdf_downloaded}")

        # Limit downloads to 2500 files
        if ammount_of_pdf_downloaded == 2500:
            print("Stopped: reached the limit of 2500 downloads.")
            return

        # Perform the actual PDF download
        download_single_pdf(url=pdf_link, filename=filename, output_folder=output_dir)

    print("All PDF links have been processed.")  # All downloads completed

    # Step 7: Post-download cleanup and validation
    files = walk_directory_and_extract_given_file_extension(
        system_path="./PDFs", extension=".pdf"
    )  # Get list of downloaded PDF files

    for pdf_file in files:
        # Validate PDF file; remove if invalid
        if not validate_pdf_file(file_path=pdf_file):
            remove_system_file(system_path=pdf_file)

        # Rename file if it contains uppercase letters
        if check_upper_case_letter(content=get_filename_and_extension(path=pdf_file)):
            print(pdf_file)  # Log file path
            dir_path = os.path.dirname(p=pdf_file)  # Directory path
            file_name = os.path.basename(p=pdf_file)  # Original file name
            new_file_name = file_name.lower()  # Convert to lowercase
            new_file_path = os.path.join(dir_path, new_file_name)  # Full new path
            os.rename(src=pdf_file, dst=new_file_path)  # Rename file on disk


# Run the script if this file is executed directly
if __name__ == "__main__":
    main()  # Call the main function
