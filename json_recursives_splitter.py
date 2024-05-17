# from langchain_community.document_loaders.csv_loader import CSVLoader
# from datetime import datetime, timedelta
from langchain_community.document_loaders import JSONLoader


# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:

    metadata["tags"] = record.get("tags")
    metadata["scp"] = record.get("scp")

    return metadata


loader = JSONLoader(
    file_path="./data/processed_json/scp-002.json",
    jq_schema=".[]",  # Extracts each object in the array
    content_key="content",  # Assumes the content is stored in the "raw_content" field
    metadata_func=metadata_func,
)

data = loader.load()


# Iterate over the loaded documents and print the content and metadata
for document in data:
    print("Content:")
    print(document.page_content)
    print("Metadata:")
    print("Tags:", document.metadata.get("tags"))
    print("SCP:", document.metadata.get("scp"))
    print("---")
