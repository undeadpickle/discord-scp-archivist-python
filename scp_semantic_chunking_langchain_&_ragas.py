# -*- coding: utf-8 -*-
"""SCP Semantic Chunking - LangChain & RAGAS.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wFh0Q3EG4qYRU0ALVxxanOsuOOE3EsVB

# Semantic Chunking with LangChain!

Today we'll be exploring Semantic Chunking!

Let's first grab the dependencies we'll be using to explore what Semantic Chunking is - and why it's useful!
"""

!pip install -qU langchain_experimental langchain_openai langchain_community langchain ragas

!pip install -qU faiss-cpu tiktoken

"""Today we'll be working with "Alice and Wonderland" as our source material - let's grab it and load it into memory."""

!wget -O scp003.txt "https://drive.google.com/uc?export=download&id=1ZoKJr3rJHsbKTzxLtdlfJbquC3HUS8eI"

with open("./scp003.txt") as f:
  scp_003 = f.read()

"""## RecursiveCharacterTextSplitter AKA "Naive Chunking"

Let's look at our documents if we use a traditional non-semantic chunking strategy!

> NOTE: The chunk size chosen here is purely for illustrative purposes.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False
)

naive_chunks = text_splitter.split_text(scp_003)

for chunk in naive_chunks[10:15]:
  print(chunk + "\n")

"""Notice how our chunks wind up split across sentences, and we have similar context split across chunks as well.

We could use a number of awesome strategies to counter this problem - but we're going to focus on Semantic Chunking today!

## Semantic Chunking

Let's start by providing our OpenAI API key - which will be required for the specific example used in this notebook.

> NOTE: You could substitute this for any embedding process. The better the embedding method - the better the results should be!
"""

import os
import getpass

os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API Key:")

"""Now let's implement the `SemanticChunker`!

We're going to be using the `percentile` threshold as an example today - but there's three different strategies you could use (descriptions provided by the [LangChain docs](https://python.langchain.com/docs/modules/data_connection/document_transformers/semantic-chunker) on Semantic Chunking):

- `percentile` (default) - In this method, all differences between sentences are calculated, and then any difference greater than the X percentile is split.

- `standard_deviation` - In this method, any difference greater than X standard deviations is split.

- `interquartile` - In this method, the interquartile distance is used to split chunks.

The basic idea is as follows:

1. Split our document into sentences (based on `.`, `?`, and `!`)
2. Index each sentence based on position
3. Add a `buffer_size` (`int`) of sentences on either side of our selected sentence
4. Calculate distances between groups of sentences
5. Merge groups based on similarity based on the above thresholds

> NOTE: This method is currently experimental and is not in a stable final form - expect updates and improvements in the coming months


"""

from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

semantic_chunker = SemanticChunker(OpenAIEmbeddings(model="text-embedding-3-large"), breakpoint_threshold_type="percentile")

"""Now we can create our documents."""

semantic_chunks = semantic_chunker.create_documents([scp_003])

"""Let's look at the chunk associated with the above naive chunks.

Notice how much more information is retained and included in each chunk.

Also notice how much larger this chunk is!
"""

for semantic_chunk in semantic_chunks:
  if "tightly, but brighter " in semantic_chunk.page_content:
    print(semantic_chunk.page_content)
    print(len(semantic_chunk.page_content))

"""## Creating a RAG Pipeline Utilizing Semantic Chunking

Let's create a RAG LCEL chain that leverages our created Semantic Chunks.

We'll start by creating our Retriever.

### Retrieval

We're going to use Meta's FAISS-backed vectorstore, and we'll use `text-embedding-3-large` (the same embedding model used to do the semantic chunking)

> NOTE: There is not specific research or reason that suggests your vectorstore embedding model should be the same as your chunking embedding model - though intuition suggests they should be the same.
"""

from langchain_community.vectorstores import FAISS

semantic_chunk_vectorstore = FAISS.from_documents(semantic_chunks, embedding=OpenAIEmbeddings(model="text-embedding-3-large"))

"""We will "limit" our semantic retriever to `k = 1` to demonstrate the power of the semantic chunking strategy while maintaining similar token counts between the semantic and naive retrieved context."""

semantic_chunk_retriever = semantic_chunk_vectorstore.as_retriever(search_kwargs={"k" : 1})

semantic_chunk_retriever.invoke("What had metallic sounds?")

"""### Augmented

We'll create a classic RAG prompt to augment our question with the retrieved context.
"""

from langchain_core.prompts import ChatPromptTemplate

rag_template = """\
Use the following context to answer the user's query. If you cannot answer, please respond with 'I don't know sucka'.

User's Query:
{question}

Context:
{context}
"""

rag_prompt = ChatPromptTemplate.from_template(rag_template)

"""### Generation

We'll use the default `ChatOpenAI` model for our generator today!
"""

from langchain_openai import ChatOpenAI

base_model = ChatOpenAI()

"""### LCEL Chain

We'll create our classic LCEL chain here to test the RAG LCEL chain!
"""

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

semantic_rag_chain = (
    {"context" : semantic_chunk_retriever, "question" : RunnablePassthrough()}
    | rag_prompt
    | base_model
    | StrOutputParser()
)

"""Let's test it out!"""

semantic_rag_chain.invoke("How does scp-003 grow?")

semantic_rag_chain.invoke("how must it be scp3 contained?")

"""These answers seem great!

Let's repeat this process for our naive chunking!
"""

naive_chunk_vectorstore = FAISS.from_texts(naive_chunks, embedding=OpenAIEmbeddings(model="text-embedding-3-large"))

"""Notice that we're going to use `k = 15` here - this is to "make it a fair comparison" between the two strategies."""

naive_chunk_retriever = naive_chunk_vectorstore.as_retriever(search_kwargs={"k" : 15})

naive_rag_chain = (
    {"context" : naive_chunk_retriever, "question" : RunnablePassthrough()}
    | rag_prompt
    | base_model
    | StrOutputParser()
)

naive_rag_chain.invoke("How does scp-003 grow?")

naive_rag_chain.invoke("how must it be scp3 contained?")

"""These answers are not bad - but they lack a certain depth that the previous answers did.

## Ragas Assessment Comparison

Let's go ahead and leverage a great tool: [Ragas](https://docs.ragas.io/en/stable/getstarted/index.html)!

We're going to split our documents utilizing a different chunking strategy to avoid any "cheating" by the naive retriever.
"""

synthetic_data_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False
)

synthetic_data_chunks = synthetic_data_splitter.create_documents([scp_003])

"""Then we will create:

- Questions - synthetically generated (`gpt-3.5-turbo`)
- Contexts - created above
- Ground Truths - synthetically generated (`gpt-4-turbo-preview`)
- Answers - generated from our Semantic RAG Chain
"""

questions = []
ground_truths_semantic = []
contexts = []
answers = []

question_prompt = """\
You are a teacher preparing a test. Please create a question that can be answered by referencing the following context.

Context:
{context}
"""

question_prompt = ChatPromptTemplate.from_template(question_prompt)

ground_truth_prompt = """\
Use the following context and question to answer this question using *only* the provided context.

Question:
{question}

Context:
{context}
"""

ground_truth_prompt = ChatPromptTemplate.from_template(ground_truth_prompt)

question_chain = question_prompt | ChatOpenAI(model="gpt-3.5-turbo") | StrOutputParser()
ground_truth_chain = ground_truth_prompt | ChatOpenAI(model="gpt-4-turbo-preview") | StrOutputParser()

for chunk in synthetic_data_chunks[10:20]:
  questions.append(question_chain.invoke({"context" : chunk.page_content}))
  contexts.append([chunk.page_content])
  ground_truths_semantic.append(ground_truth_chain.invoke({"question" : questions[-1], "context" : contexts[-1]}))
  answers.append(semantic_rag_chain.invoke(questions[-1]))

"""We'll format those into a dataset!"""

from datasets import load_dataset, Dataset

qagc_list = []

for question, answer, context, ground_truth in zip(questions, answers, contexts, ground_truths_semantic):
  qagc_list.append({
      "question" : question,
      "answer" : answer,
      "contexts" : context,
      "ground_truth" : ground_truth
  })

eval_dataset = Dataset.from_list(qagc_list)

eval_dataset

"""Now we can implement Ragas metrics and evaluate our created dataset."""

from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)

"""You can check out our [previous webinar](https://www.youtube.com/watch?v=Anr1br0lLz8) about Ragas to learn a bit more about these metrics."""

from ragas import evaluate

result = evaluate(
    eval_dataset,
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
        context_recall,
    ],
)

result

results_df = result.to_pandas()
results_df

"""The results indicate that this is a "fine" result - largely.

But let's compare to our naive strategy!
"""

for chunk in synthetic_data_chunks[10:20]:
  questions.append(question_chain.invoke({"context" : chunk.page_content}))
  contexts.append([chunk.page_content])
  ground_truths_semantic.append(ground_truth_chain.invoke({"question" : questions[-1], "context" : contexts[-1]}))
  answers.append(naive_rag_chain.invoke(questions[-1]))

naive_result = evaluate(
    eval_dataset,
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
        context_recall,
    ],
)

naive_result

naive_results_df = result.to_pandas()
naive_results_df

"""As we can see this result is noticeably worse!"""

naive_result

result