# Phase 1: Redis Setup

Ensure you have a Redis server running. (You can use Docker: `docker run --name quiz-redis -p 6379:6379 -d redis`)

## Example: Connecting to Redis in Python

```python
import redis

# Connect to local Redis instance (default Docker port)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Test connection
try:
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError:
    print("Failed to connect to Redis.")
```

Add this code to your project to verify your Redis connection before proceeding to the next phase.

--- 

# Phase 2: Pinecone & Nomic Embeddings Setup

You need a Pinecone account and API key. Replace the placeholders in the code below with your actual credentials and desired index name.

## Example: Initializing Pinecone and Nomic Embeddings

```python
import pinecone
from langchain_nomic import NomicEmbeddings

# Initialize Pinecone
pinecone.init(api_key="YOUR_PINECONE_API_KEY", environment="us-west1-gcp")
index = pinecone.Index("educational-content")  # Replace with your index name

# Initialize Nomic Embeddings
embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5")
```

- Make sure the Pinecone index exists in your account before running this code.
- You can create an index via the Pinecone dashboard or API.

--- 

# Phase 3: BM25 Sparse Retriever Setup

BM25 is a keyword-based retrieval method that complements dense vector search. We'll use LangChain's BM25 retriever for this purpose.

## Example: Initializing BM25 Retriever

```python
from langchain_community.vectorstores import BM25Retriever

# Example list of document chunks (replace with your actual chunks)
documents = [
    "This is the first document chunk.",
    "Another chunk of educational content.",
    "Further information for retrieval testing."
]

bm25_retriever = BM25Retriever.from_texts(documents)

# Test retrieval
results = bm25_retriever.get_relevant_documents("educational content")
for doc in results:
    print(doc)
```

- Replace the `documents` list with your actual document chunks when available.
- This retriever can be used in combination with Pinecone for hybrid retrieval.

--- 