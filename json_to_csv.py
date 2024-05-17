import csv
import json
import os
from datetime import datetime
import uuid
import re

# Load the processed JSON files from the directory
json_dir = "./data/processed_json/"
csv_dir = "./data/csv/"

# Create the output directory for CSV files if it doesn't exist
os.makedirs(csv_dir, exist_ok=True)

# Define the CSV column names
csv_columns = [
    "id",
    "title",
    "content",
    "rating",
    "created_at",
    "creator",
    "url",
    "tags",
    "references",
]

# Iterate over each JSON file in the directory
for filename in os.listdir(json_dir):
    if filename.endswith(".json"):
        # Load the JSON data from the file
        with open(os.path.join(json_dir, filename), "r") as json_file:
            scp_data = json.load(json_file)

        # Extract the relevant metadata from the JSON data
        title = scp_data.get("title", "")
        content = scp_data.get("content", "")
        rating = scp_data.get("rating", 0)
        created_at = scp_data.get("created_at", "")
        creator = scp_data.get("creator", "")
        url = scp_data.get("url", "")
        tags = ", ".join(scp_data.get("tags", [])) if scp_data.get("tags") else ""
        references = (
            ", ".join(scp_data.get("references", []))
            if scp_data.get("references")
            else ""
        )

        # Generate a unique identifier
        unique_id = str(uuid.uuid4())

        # Remove whitespace or line breaks greater than 2 from the content
        content = re.sub(r"\s{3,}", " ", content)

        # Extract the SCP number from the title and remove preceding zeros
        scp_number = title.split("-")[-1].lstrip("0") if "-" in title else ""

        # Create a CSV file for the current SCP with the formatted filename
        csv_filename = f"scp_{scp_number}.csv"
        csv_path = os.path.join(csv_dir, csv_filename)

        # Write the data to the CSV file
        with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            writer.writeheader()
            writer.writerow(
                {
                    "id": unique_id,
                    "title": title,
                    "content": content,
                    "rating": rating,
                    "created_at": created_at,
                    "creator": creator,
                    "url": url,
                    "tags": tags,
                    "references": references,
                }
            )

print("CSV files created successfully.")
