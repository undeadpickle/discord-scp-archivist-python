# Redis memory
import json
import logging
from bs4 import BeautifulSoup
import spacy
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import redis

# Define ANSI escape codes for colors
USER_INPUT_COLOR = "\033[92m"  # Green
CHATBOT_COLOR = "\033[94m"  # Blue
LOGGING_COLOR = "\033[90m"  # Dark Gray
ERROR_COLOR = "\033[91m"  # Red
RESET_COLOR = "\033[0m"

# Load environment variables from .env file
load_dotenv()

# Access variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()
client.api_key = openai_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
index_name = "scp-archivist"
# logging.info(f"Describe Index: {pc.describe_index("scp-archivist")}")


# Load the pre-trained SpaCy English model
logging.info("Loading SpaCy model...")
nlp = spacy.load("en_core_web_sm")
logging.info("SpaCy model loaded successfully.")


def preprocess_text(text):
    """
    Preprocess the text using BeautifulSoup and SpaCy.
    """
    try:
        # Remove HTML tags and escape sequences using BeautifulSoup
        soup = BeautifulSoup(text, "lxml")
        cleaned_text = soup.get_text()
        logging.info(f"BeautifulSoup processed text: {cleaned_text[:100]}...")

        # Tokenize the text, lemmatize, and remove stop words using SpaCy
        doc = nlp(cleaned_text)
        tokens = [
            token.lemma_.lower()
            for token in doc
            if not token.is_stop and not token.is_punct
        ]
        logging.info(f"SpaCy processed tokens: {tokens[:10]}...")

        # Join the tokens back into a string
        processed_text = " ".join(tokens)
        logging.info(f"Preprocessed text: {processed_text[:100]}...")

        return processed_text
    except Exception as e:
        logging.error(f"Error preprocessing text: {e}")
        raise


def save_processed_text(processed_text, scp_number):
    """
    Save the processed text as a txt file in the data directory.
    """
    try:
        # Create the data directory if it doesn't exist
        os.makedirs("./data", exist_ok=True)
        # Create the file path
        file_path = f"./data/scp_{scp_number}_processed.txt"

        # Save the processed text to the file
        with open(file_path, "w") as file:
            file.write(processed_text)

        logging.info(f"Processed text saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving processed text: {e}")
        raise


def save_processed_query(processed_query, query):
    """
    Save the processed query as a txt file in the data directory.
    """
    try:
        # Create the data directory if it doesn't exist
        os.makedirs("./data", exist_ok=True)

        # Create the file path
        file_path = f"./data/query_{query.replace(' ', '_')}_processed.txt"

        # Save the processed query to the file
        with open(file_path, "w") as file:
            file.write(processed_query)

        logging.info(f"Processed query saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving processed query: {e}")
        raise


def create_embedding(text):
    """
    Create an embedding for the given text using the OpenAI API.
    """
    try:
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        embedding = response.data[0].embedding
        logging.info(f"Embedding created successfully. Shape: {len(embedding)}")
        return embedding
    except Exception as e:
        logging.error(f"Error creating embedding: {e}")
        raise


def upsert_to_pinecone(entry):
    """
    Upsert an SCP entry to the Pinecone index.
    """
    try:
        # Extract the required fields from the entry
        scp_number = entry["scp_number"]
        title = entry["title"]
        description = entry["description"]
        created_at = entry["created_at"]
        creator = entry["creator"]
        url = entry["url"]
        tags = entry["tags"]
        references = entry["references"]
        series = entry["series"]

        # Preprocess the title and description
        processed_title = preprocess_text(title)
        processed_description = preprocess_text(description)

        # Log the preprocessed title and description
        logging.info(f"Preprocessed Title: {processed_title}")
        logging.info(f"Preprocessed Description: {processed_description}")

        # Save the processed description as a txt file
        # save_processed_text(processed_description, scp_number)

        # Create embeddings for the title and description
        title_embedding = create_embedding(processed_title)
        description_embedding = create_embedding(processed_description)

        # Create a unique ID for the entry
        entry_id = f"scp-{scp_number}"

        # Create the metadata dictionary
        metadata = {
            "scp_number": scp_number,
            "created_at": created_at,
            "creator": creator,
            "url": url,
            "tags": tags,
            "references": references,
            "series": series,
        }

        # Upsert the entry to the Pinecone index
        vectors = [
            (entry_id, title_embedding, metadata),
            (entry_id, description_embedding, metadata),
        ]
        index = pc.Index(index_name)
        index.upsert(vectors)
        logging.info(f"Entry {entry_id} upserted to Pinecone successfully.")

        # Log the embedded title and description
        # logging.info(f"Embedded Title: {title_embedding}")
        # logging.info(f"Embedded Description: {description_embedding}")
    except Exception as e:
        logging.error(f"Error upserting entry to Pinecone: {e}")
        raise


def query_pinecone(query, top_k=5):
    """
    Query the Pinecone index and retrieve the most similar entries.
    """
    try:
        # Preprocess the query
        processed_query = preprocess_text(query)
        logging.info(f"Preprocessed query: {processed_query}")

        # Save the processed query as a txt file
        # save_processed_query(processed_query, query)

        # Create an embedding for the query
        query_embedding = create_embedding(processed_query)
        logging.info(
            f"Query embedding created successfully. Shape: {len(query_embedding)}"
        )

        # Query the Pinecone index
        index = pc.Index(index_name)
        results = index.query(
            vector=query_embedding, top_k=top_k, include_metadata=True
        )
        logging.info(
            f"Pinecone query completed successfully. Retrieved {len(results.matches)} matches."
        )

        # Extract the entry IDs and similarity scores from the results
        entries = [(match.id, match.score) for match in results.matches]
        logging.info(f"Retrieved entries: {entries}")

        return entries
    except Exception as e:
        logging.error(f"Error querying Pinecone: {e}")
        raise


def generate_response(query, retrieved_entries, conversation_id, conversation_history):
    try:
        prompt = f"Query: {query}\n\n"

        # Integrate retrieved entries directly into the context
        if retrieved_entries:
            prompt += "While considering these related SCP entries:\n"
            for entry_id, score in retrieved_entries:
                prompt += f"- {entry_id} (Similarity: {score:.2f})\n"
        else:
            prompt += (
                "I don't have detailed information about that SCP in my records. "
                "My general knowledge might be inaccurate, so I recommend checking the "
                "official SCP Wiki for reliable information.\n"
            )

        prompt += "\nPrevious Conversation:\n"
        for i, (prev_query, prev_response) in enumerate(conversation_history, start=1):
            prompt += f"User: {prev_query}\n"
            prompt += f"Assistant: {prev_response}\n\n"

        # Emphasize direct answers and context utilization
        prompt += (
            "Provide a detailed response to the user's query, making sure to "
            "directly answer any specific questions. Utilize the related SCP entries "
            "and previous conversation to inform your response."
        )

        logging.info(f"Generating response for query: {query}")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledgeable but snarky and bitter assistant that begrudgingly provides detailed responses to queries using information from retrieved SCP entries and conversation history. Your responses should directly address the query, provide clear answers when asked, and build upon the previous context provided by the user.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        generated_response = response.choices[0].message.content
        # logging.info(f"Generated response: {generated_response}")

        # Store the conversation history in Redis
        logging.info(
            f"Storing conversation history in Redis for conversation_id: {conversation_id}"
        )
        r.hset(f"conversation:{conversation_id}", "query", query)
        r.hset(f"conversation:{conversation_id}", "response", generated_response)

        # Set expiration time to 24 hours (optional)
        r.expire(f"conversation:{conversation_id}", 86400)

        logging.info(
            f"Conversation history stored in Redis: conversation_id={conversation_id}, query={query}, response={generated_response}"
        )

        return generated_response
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        raise


if index_name not in pc.list_indexes().names():
    logging.info(f"Index '{index_name}' does not exist. Creating the index.")
    pc.create_index(
        name=index_name,
        dimension=1536,  # This should match the dimensionality of your embeddings
        metric="cosine",  # Adjust metric if necessary
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

    # Load the JSON data from the local file
    logging.info("Loading JSON data from local file...")
    with open("./data/scp_data_test.json") as file:
        data = json.load(file)
    logging.info(f"JSON data loaded successfully. Number of entries: {len(data)}")

    # Process each SCP entry
    for scp_number, entry_data in data.items():
        # Extract the required fields from the entry
        scp_entry = {
            "scp_number": int(scp_number.split("-")[1]),
            "title": entry_data["title"],
            "description": entry_data["raw_content"],
            "created_at": entry_data["created_at"],
            "creator": entry_data["creator"],
            "url": entry_data["url"],
            "tags": entry_data["tags"],
            "references": entry_data["references"],
            "series": entry_data["series"],
        }

        # Upsert the entry to the Pinecone index
        upsert_to_pinecone(scp_entry)

else:
    logging.info(
        f"Index '{index_name}' already exists. Skipping data preprocessing and upserting."
    )


# Connect to Redis
r = redis.Redis(host="localhost", port=6379, db=0)
r.ping()


# Start the interactive prompt loop
conversation_id = 1
conversation_history = []
while (
    user_input := input(
        f"{USER_INPUT_COLOR}Enter a prompt (or 'q' to quit): {RESET_COLOR}"
    ).lower()
) != "q":
    query = user_input
    similar_entries = query_pinecone(
        query, top_k=5
    )  # Increase the number of retrieved entries

    logging.info(f"Generated Query: {query}")
    generated_response = generate_response(
        query, similar_entries, conversation_id, conversation_history
    )
    print(f"\n{CHATBOT_COLOR}Generated Response: {generated_response}{RESET_COLOR}\n")

    # Update conversation history
    conversation_history.append((query, generated_response))

    # Retrieve conversation history from Redis
    redis_conversation_history = []
    logging.debug(
        f"Retrieving conversation history from Redis for conversation_id: {conversation_id}"
    )
    for i in range(1, conversation_id):
        stored_query = r.hget(f"conversation:{i}", "query")
        stored_response = r.hget(f"conversation:{i}", "response")
        if stored_query and stored_response:
            redis_conversation_history.append(
                (stored_query.decode(), stored_response.decode())
            )

    if redis_conversation_history:
        print(f"{LOGGING_COLOR}=== Conversation History ==={RESET_COLOR}")
        for query, response in redis_conversation_history:
            print(f"{LOGGING_COLOR}[Conversation {conversation_id - 1}]{RESET_COLOR}")
            print(f"{LOGGING_COLOR}  Query: {query}{RESET_COLOR}")
            print(f"{LOGGING_COLOR}  Response: {response}{RESET_COLOR}\n")
        print(f"{LOGGING_COLOR}----------------------------{RESET_COLOR}\n")

    conversation_id += 1
