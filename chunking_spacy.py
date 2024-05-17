# Chunking strategies url: https://www.pinecone.io/learn/chunking-strategies/
import os  # Importing the os module for interacting with the operating system
import glob  # Importing the glob module to find all the pathnames matching a specified pattern
import json  # Importing the json module for JSON manipulation
from openai import OpenAI  # Importing the OpenAI class from the openai package
from langchain_text_splitters import (
    SpacyTextSplitter,
)  # Importing spaCy chunking from langchain.text_splitter
from langchain_openai import (
    OpenAIEmbeddings,
)  # Importing OpenAIEmbeddings from langchain_openai

# Creating an OpenAI client instance
client = OpenAI()

# Directory paths for input and output folders
input_folder = "./data/txt"
output_folder = "./data/txt/output_spacy"
os.makedirs(
    output_folder, exist_ok=True
)  # Create the output folder if it doesn't exist


def load_text_files(input_folder):
    # Find all text files in the input folder
    file_paths = glob.glob(os.path.join(input_folder, "*.txt"))
    texts = {}  # Dictionary to hold file names and their content
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            file_name = os.path.basename(file_path)  # Get the file name from the path
            texts[file_name] = (
                file.read()
            )  # Read the file content and store it in the dictionary
            print("load_text_files")  # Print a message for debugging purposes
    return texts  # Return the dictionary of file names and contents


def get_embeddings(chunks):
    embeddings = []  # List to hold the embeddings
    for chunk in chunks:
        # Create embeddings for each chunk using the OpenAI API
        response = client.embeddings.create(input=chunk, model="text-embedding-3-small")
        embeddings.append(
            response.data[0].embedding
        )  # Append the embedding to the list
        print("get_embeddings")  # Print a message for debugging purposes
    return embeddings  # Return the list of embeddings


def save_combined_file(file_name, chunks, embeddings, output_folder):
    output_path = os.path.join(output_folder, file_name)  # Create the output file path
    combined_data = []  # List to hold combined chunks and embeddings
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        combined_data.append(
            {"id": i, "text": chunk, "embedding": embedding}
        )  # Add each chunk and its embedding with an ID
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(
            combined_data, output_file, ensure_ascii=False, indent=2
        )  # Save the combined data to a JSON file
        print("save_combined_file")  # Print a message for debugging purposes


def chunk_text_spacy(text):
    """
    Splits text into spaCy meaningful chunks using Langchain.
    """
    # Create a spaCy instance with OpenAI embeddings
    text_splitter = SpacyTextSplitter(OpenAIEmbeddings(), chunk_size=1000)
    docs = text_splitter.split_text(text)  # Pass 'text' directly, not as a list
    print(len(docs))  # Print the number of documents created
    chunks = docs  # 'docs' is already a list of chunks
    return chunks  # Return the list of chunks


def main():
    print("main")  # Print a message for debugging purposes
    texts = load_text_files(input_folder)  # Load text files from the input folder
    for file_name, text in texts.items():
        chunks = chunk_text_spacy(text)  # Split the text into spaCy chunks
        embeddings = get_embeddings(chunks)  # Get embeddings for each chunk
        output_file_name = (
            f"scp-{file_name.split('-')[1]}"  # Create an output file name
        )
        save_combined_file(
            output_file_name, chunks, embeddings, output_folder
        )  # Save the combined chunks and embeddings to a file


if __name__ == "__main__":
    main()  # Run the main function if the script is executed directly
