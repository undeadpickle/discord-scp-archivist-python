import requests
import json
import os
from bs4 import BeautifulSoup

# Load the large JSON file from the URL
url = "https://raw.githubusercontent.com/scp-data/scp-api/main/docs/data/scp/items/content_series-1.json"
response = requests.get(url)
data = json.loads(response.text)

# Create the output directory if it doesn't exist
output_dir = "./data/processed_json/"
os.makedirs(output_dir, exist_ok=True)

# Iterate over each SCP object in the JSON data
for scp_number, scp_data in data.items():
    # Remove unwanted properties
    unwanted_properties = [
        "history",
        "images",
        "page_id",
        "scp",
        "hubs",
        "domain",
        "raw_source",
    ]
    for prop in unwanted_properties:
        if prop in scp_data:
            del scp_data[prop]

    # Remove unwanted HTML using Beautiful Soup
    if "raw_content" in scp_data:
        soup = BeautifulSoup(scp_data["raw_content"], "html.parser")
        content = soup.get_text()

        # Find the position of "Item #: ..." and update the content
        item_index = content.find("Item #:")
        if item_index != -1:
            content = content[item_index:]

        # Rename "raw_content" field to "content"
        scp_data["content"] = content
        del scp_data["raw_content"]

    # Save the processed JSON file
    output_file = f"{output_dir}{scp_number.lower()}.json"
    with open(output_file, "w") as file:
        json.dump(scp_data, file, indent=2)

print("JSON files processed and saved successfully.")
