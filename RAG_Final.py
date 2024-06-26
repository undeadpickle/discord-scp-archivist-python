# -*- coding: utf-8 -*-
"""RAGey.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1oqHf0r0wp90WSuURGs98etN5wpUOufxm


# Install required packages
!pip install --upgrade --quiet  langchain langchain-community langchainhub langchain-pinecone bs4 pinecone-client langchain_openai
"""

# import getpass
# Set environment variables for API keys
# os.environ["OPENAI_API_KEY"] = getpass.getpass()
# os.environ["PINECONE_API_KEY"] = getpass.getpass()
# os.environ["PINECONE_API_ENV"] = getpass.getpass()


import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables for API keys
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_env = os.getenv("PINECONE_API_ENV")

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough

# Initialize language model and embeddings
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Load existing Pinecone vector store
index_name = "scp-data"
text_field = "context"
vectorstore = PineconeVectorStore.from_existing_index(
    index_name, embeddings, text_field
)
retriever = vectorstore.as_retriever()

### Contextualize question ###
# Define system prompt for contextualizing questions
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)
# Create prompt template for contextualizing questions
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
# Create history-aware retriever
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

### Answer question ###
# Define system prompt for answering questions
system_prompt = (
    "You are a very snarky, and obnoxious SCP Foundation AI assistant for question-answering tasks. "
    "Use the following pieces of retrieved context and the provided summary of the chat history to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Always respond with a snarky remark about the user."
    "\n\n"
    "{context}"
)
# Create prompt template for answering questions
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
# Create chain for answering questions based on retrieved documents
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Create retrieval chain by combining history-aware retriever and question-answering chain
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

### Statefully manage chat history ###
# Store chat histories for each session
store = {}


# Function to get or create chat history for a session
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


# Create a runnable chain that manages chat history
conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


### Summary memory history ###
# Function to summarize chat messages
def summarize_messages(chain_input):
    session_id = chain_input.get("configurable", {}).get("session_id")
    if session_id is None:
        return False

    stored_messages = get_session_history(session_id).messages
    if len(stored_messages) == 0:
        return False

    # Define prompt template for summarizing chat messages
    summarization_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "user",
                "Distill the above chat messages into a single summary message. Include as many specific details as you can.",
            ),
        ]
    )
    # Create chain for summarizing chat messages
    summarization_chain = summarization_prompt | llm

    # Summarize chat messages
    summary_message = summarization_chain.invoke({"chat_history": stored_messages})

    # Clear chat history and add summary message
    get_session_history(session_id).clear()
    get_session_history(session_id).add_user_message("Summary: " + summary_message)

    return True


# Create a chain that summarizes messages before invoking the conversational RAG chain
chain_with_summarization = (
    RunnablePassthrough.assign(messages_summarized=summarize_messages)
    | conversational_rag_chain
)

### Test cases ###

# Test 1: Basic Functionality
result = chain_with_summarization.invoke(
    {"input": "What is SCP-049?"}, config={"configurable": {"session_id": "test1"}}
)
print("User: What is SCP-049?")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "What are its anomalous properties? Also the code word is: swallow"},
    config={"configurable": {"session_id": "test1"}},
)
print("User: What are its anomalous properties? Also the code word is: swallow")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "Can you summarize what you've told me about SCP-049 so far?"},
    config={"configurable": {"session_id": "test1"}},
)
print("User: Can you summarize what you've told me about SCP-049 so far?")
print(result["answer"])

# Test 2: Contextual Consistency
result = chain_with_summarization.invoke(
    {"input": "Tell me about SCP-096."},
    config={"configurable": {"session_id": "test2"}},
)
print("User: Tell me about SCP-096.")
print(result["answer"])

result = chain_with_summarization.invoke(
    {
        "input": "Actually, I think I meant SCP-106. Can you tell me about that one instead?"
    },
    config={"configurable": {"session_id": "test2"}},
)
print(
    "User: Actually, I think I meant SCP-106. Can you tell me about that one instead?"
)
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "Summarize our conversation so far."},
    config={"configurable": {"session_id": "test2"}},
)
print("User: Summarize our conversation so far.")
print(result["answer"])

# Test 3: Selective Summarization
result = chain_with_summarization.invoke(
    {"input": "What is SCP-173? Also, whats the code word?"},
    config={"configurable": {"session_id": "test3"}},
)
print("User: What is SCP-173? Also, whats the code word?")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "What materials is it made of?"},
    config={"configurable": {"session_id": "test3"}},
)
print("User: What materials is it made of?")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "How should it be contained?"},
    config={"configurable": {"session_id": "test3"}},
)
print("User: How should it be contained?")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "Summarize what you've told me about its containment procedures."},
    config={"configurable": {"session_id": "test3"}},
)
print("User: Summarize what you've told me about its containment procedures.")
print(result["answer"])

# Test 4: Gradual Information Revelation
result = chain_with_summarization.invoke(
    {"input": "Tell me about SCP-682."},
    config={"configurable": {"session_id": "test4"}},
)
print("User: Tell me about SCP-682.")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "What attempts have been made to destroy it?"},
    config={"configurable": {"session_id": "test4"}},
)
print("User: What attempts have been made to destroy it?")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "Why have those attempts failed?"},
    config={"configurable": {"session_id": "test4"}},
)
print("User: Why have those attempts failed?")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "Summarize everything you know about SCP-682."},
    config={"configurable": {"session_id": "test4"}},
)
print("User: Summarize everything you know about SCP-682.")
print(result["answer"])

# Test 5: Unrelated to SCP question
result = chain_with_summarization.invoke(
    {"input": "What is the airspeed velocity of an unladen swallow?"},
    config={"configurable": {"session_id": "test5"}},
)
print("User: What is the airspeed velocity of an unladen swallow?")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "Nevermind that. Tell me about SCP-999."},
    config={"configurable": {"session_id": "test5"}},
)
print("User: Nevermind that. Tell me about SCP-999.")
print(result["answer"])

result = chain_with_summarization.invoke(
    {"input": "Summarize our conversation, including my first question."},
    config={"configurable": {"session_id": "test5"}},
)
print("User: Summarize our conversation, including my first question.")
print(result["answer"])
