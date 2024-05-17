import os
import glob
import json

# from openai import OpenAI

# client = OpenAI()


# Directory paths
input_folder = "./data/txt"
output_folder = "./data/txt/output_fixedsize_overlap"
os.makedirs(output_folder, exist_ok=True)


def load_text_files(input_folder):
    file_paths = glob.glob(os.path.join(input_folder, "*.txt"))
    texts = {}
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            file_name = os.path.basename(file_path)
            texts[file_name] = file.read()
            print("load_text_files")
    return texts


def chunk_text(text, chunk_size=500, overlap_size=100):
    words = text.split()
    chunks = []
    start_index = 0
    while start_index < len(words):
        end_index = min(start_index + chunk_size, len(words))
        chunks.append(" ".join(words[start_index:end_index]))
        start_index += chunk_size - overlap_size
    print("chunk_text")
    return chunks


# def get_embeddings(chunks):
#     embeddings = []
#     for chunk in chunks:
#         response = client.embeddings.create(input=chunk, model="text-embedding-3-small")
#         embeddings.append(response.data[0].embedding)
#         print("get_embeddings")
#     return embeddings


def save_combined_file(
    file_name, chunks, output_folder
):  # Removed embeddings from arguments
    output_path = os.path.join(output_folder, file_name)
    combined_data = []
    for i, chunk in enumerate(chunks):
        combined_data.append(
            {"chunk_id": i, "chunk_text": chunk}  # Removed embedding from dictionary
        )
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(combined_data, output_file, ensure_ascii=False, indent=2)
        print("save_combined_file")


def main():
    print("main")
    texts = load_text_files(input_folder)

    for file_name, text in texts.items():
        chunks = chunk_text(text)
        # embeddings = get_embeddings(chunks)  # Commenting out embedding generation
        output_file_name = f"scp-{file_name.split('-')[1]}"
        save_combined_file(
            output_file_name, chunks, output_folder
        )  # Removed embeddings from arguments


if __name__ == "__main__":
    main()
