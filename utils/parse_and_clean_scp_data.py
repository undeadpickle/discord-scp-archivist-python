import json
from bs4 import BeautifulSoup
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Define a function to clean HTML content using BeautifulSoup
def clean_html(raw_html):
    """
    Remove HTML tags and normalize text from raw HTML content.

    Args:
        raw_html (str): The raw HTML content.

    Returns:
        str: Cleaned text content.
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()


# Define a function to load and parse the JSON data
def load_and_clean_json(file_path):
    """
    Load JSON data from a file, clean HTML content, and prepare it for database insertion.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        list: A list of cleaned SCP entries.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file: {e}")
        return []

    cleaned_data = []
    for scp_id, scp_data in data.items():
        # Clean the raw_content field if it exists
        if "raw_content" in scp_data:
            scp_data["clean_content"] = clean_html(scp_data["raw_content"])
            del scp_data["raw_content"]  # Remove raw_content field

        # Remove raw_source field if it exists
        if "raw_source" in scp_data:
            del scp_data["raw_source"]

        # Remove history field if it exists
        if "history" in scp_data:
            del scp_data["history"]

        # Add the SCP ID to the data
        scp_data["scp_id"] = scp_id
        cleaned_data.append(scp_data)

    return cleaned_data


# Main function to execute the script
if __name__ == "__main__":
    # Define the path to the JSON file (update this path as necessary)
    json_file_path = "./data/scp_data_example.json"

    # Load and clean the JSON data
    cleaned_scp_entries = load_and_clean_json(json_file_path)

    # Print the first entry to verify the cleaning process
    if cleaned_scp_entries:
        logging.info(f"First cleaned SCP entry: {cleaned_scp_entries[0]}")
        logging.info("Data loaded and cleaned successfully.")
    else:
        logging.error("No data was loaded and cleaned.")
