# This is a long document we can split up.
with open("./data/txt/SCP-002.txt") as f:
    state_of_the_union = f.read()

from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

text_splitter = SemanticChunker(OpenAIEmbeddings())
docs = text_splitter.create_documents([state_of_the_union])
print(docs[0].page_content)
