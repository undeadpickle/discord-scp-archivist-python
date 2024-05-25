# Discord SCP Archivist Bot (Python)

This Discord bot, named The SCP Archivist, serves as an interactive guide to the SCP Foundation universe within Discord servers. Powered by Python and the `discord.py` library, it leverages the power of AI and natural language processing to provide engaging and informative responses to user queries about SCPs.

The bot utilizes the Langchain framework to connect with OpenAI's language models and embeddings, storing and retrieving information from a Pinecone vector database for accurate and contextually relevant responses. It engages users with accurate SCP lore and data through features like dynamic command handling, event management, slash commands, and RAG querying.

## Purpose

The primary goal of this project is to create a comprehensive and engaging SCP Foundation chatbot experience on Discord. The bot should be able to:

- Understand and respond to user queries about SCPs in a conversational manner
- Retrieve and present relevant information from a vast dataset of SCP articles
- Engage users in discussions and provide insightful details about the SCP universe

## Features

- **AI-Powered Responses:** Utilizes OpenAI's GPT models for generating human-like text and answering user questions
- **Semantic Search:** Employs OpenAI embeddings and a Pinecone vector database for efficient and accurate retrieval of SCP information
- **Contextual Awareness:** Maintains conversation history to provide contextually relevant responses
- **Dynamic Command Handling:** Allows for easy expansion with new commands and features
- **Error Handling:** Implements robust error handling to ensure smooth operation
- **Session Management:** Supports multiple user sessions simultaneously
- **Slash Commands:** Utilizes the newer Discord slash command interface, with easy command deployment
- **Event-Driven Architecture:** Events are handled through modular files, ensuring easy addition of new event responses

## Project Structure

```
discord-scp-archivist-python/
├── .env
├── .gitignore
├── README.md
├── bot.py
├── commands/
│   └── utility/
│       ├── reload.py
│       ├── server.py
│       ├── user.py
│       └── scp.py
├── deploy_commands.py
├── data/
│   ├── scpData.json
│   └── scpTimestamps.json
├── events/
│   ├── on_message.py
│   └── on_ready.py
├── requirements.txt
└── scp_chatbot_json_process+retrieval.py
```

## Development Environment

- **Environment:**
  - Python 3.8+
  - pip (package installer)
- **Dependencies:**
  - discord.py
  - langchain
  - langchain-community
  - openai
  - pinecone-client
  - pinecone-text
  - bs4
  - tqdm
  - tiktoken
- **Hosting:** Heroku
- **Databases:** Pinecone vector database

## Installation

1. Clone the repository
2. Change to the project directory
3. Create and activate a virtual environment
4. Install the required dependencies: `pip install -r requirements.txt`
5. Set up environment variables in the `.env` file
6. Run the bot: `python bot.py`

## Bot Details

- **Name:** The SCP Archivist
- **Bot Profile About Me:** I am The SCP Archivist, the silent sentinel of the Foundation's darkest corridors. Venture with me into the labyrinth of the unknown, where the lore of SCPs unfolds like ancient scrolls. Together, we'll navigate the cryptic rituals and tales that bind the haunted world of containment and chaos, revealing truths as profound as they are perilous.
- **Discord Server URL:** https://discord.com/channels/1232117088508710912/1232117088508710915
- **Client ID:** 1232113446766641244
- **Guild ID:** 1232117088508710912
- **Discord Bot scopes:** `bot, applications.commands, messages.read`
- **Discord Bot permissions:** `Send Messages, Read Message History, Read Messages/View Channels`

## Core Chatbot Logic

**scp_chatbot_json_process+retrieval.py:**

1. **Data Processing:**

   - Loads SCP data from JSON files
   - Extracts relevant information and metadata
   - Splits text into chunks for embedding and storage

2. **Embedding and Vector Database:**

   - Uses OpenAI embeddings to generate vector representations
   - Stores vectors and metadata in Pinecone
   - Implements batch processing for efficiency

3. **Retrieval and Response Generation:**
   - Receives user queries via Discord
   - Converts queries to vector representations
   - Performs similarity search in Pinecone to retrieve relevant info
   - Uses RAG querying and OpenAI GPT to generate contextual responses
   - Maintains stateful chat history for continuous conversations

## Command Handling

- Commands are modular and stored in the `commands` directory
- Each command is defined in a separate file
- The `deploy_commands.py` script registers slash commands with Discord's API
- Example commands:
  - `!scp <SCP number or name>`: Retrieves information about a specific SCP
  - `!help`: Displays available commands and descriptions

## Event Handling

- Events are managed through modules in the `events` directory
- Includes handling for events like `on_message` and `on_ready`
- The bot responds appropriately to different events during operation

## Error Handling

The bot handles potential errors gracefully:

- Invalid SCP queries: When the provided SCP number or name is not found
- API errors: Issues connecting to OpenAI or Pinecone
- Robust error handling within command and event handling scripts

## Session Management

The bot manages user sessions to maintain conversation history and provide context-aware responses:

- Keeps track of the last five messages for each user
- Stores user histories in memory (RAM) of the host server
- Implements periodic cleanup tasks to manage memory usage

## Deployment

The bot can be deployed on platforms like Heroku:

1. Set up Heroku CLI and create a Heroku app
2. Configure environment variables
3. Deploy the app using `git push heroku main`
4. Scale the dynos as needed

## Development Practices

- **Modular Design:** Code is organized into modules for separation of concerns
- **Security:** Sensitive data stored in `.env` files, following best practices
- **Error Handling & Logging:** Robust error handling and logging for debugging
- **Dependency Management:** Uses `requirements.txt` for Python dependencies
- **Code Style:** Follows PEP 8 guidelines for Python

## Future Enhancements

- **Rate Limiting:** To manage API usage costs
- **Tiered Access:** Paid version for extended features and higher limits
- **Multimedia Integration:** Incorporating images, audio, and other media
- **User Profiles:** Customized interactions and tracking of user SCP knowledge
- **Cross-Platform:** Expanding availability to platforms besides Discord

## License

This project is licensed under the [MIT License](LICENSE).
