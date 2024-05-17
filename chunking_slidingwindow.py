import os
import glob
import json
from openai import OpenAI

client = OpenAI()


# Directory paths
input_folder = "./data/txt"
output_folder = "./data/txt/output_slidingwindow"
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


def chunk_text(text, chunk_size=500, stride=250):
    words = text.split()
    chunks = []
    for i in range(0, len(words), stride):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
    print("chunk_text")
    return chunks


def get_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(input=chunk, model="text-embedding-3-small")
        embeddings.append(response.data[0].embedding)
        print("get_embeddings")
    return embeddings


def save_combined_file(file_name, chunks, embeddings, output_folder):
    output_path = os.path.join(output_folder, file_name)
    combined_data = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        combined_data.append(
            {"chunk_id": i, "chunk_text": chunk, "chunk_embedding": embedding}
        )
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(combined_data, output_file, ensure_ascii=False, indent=2)
        print("save_combined_file")


def main():
    print("main")
    texts = load_text_files(input_folder)

    for file_name, text in texts.items():
        chunks = chunk_text(text)
        embeddings = get_embeddings(chunks)
        output_file_name = f"scp-{file_name.split('-')[1]}"
        save_combined_file(output_file_name, chunks, embeddings, output_folder)


if __name__ == "__main__":
    main()
