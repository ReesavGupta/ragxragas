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

# Phase 4: FastAPI Endpoint for Document Upload and Chunking

We'll create a FastAPI endpoint to accept file uploads, chunk the document, and prepare the chunks for storage in Pinecone and BM25.

## Example: FastAPI Upload and Chunking Endpoint

```python
from fastapi import FastAPI, File, UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = FastAPI()

@app.post("/upload/")
async def upload_doc(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode()
    # Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = splitter.split_text(text)
    # For now, just return the number of chunks
    return {"message": f"Uploaded and split into {len(chunks)} chunks."}
```

- In the next phase, we'll store these chunks in Pinecone and BM25.
- You can test this endpoint with a tool like curl or Postman.

--- 

# Phase 5: Store Chunks in Pinecone and BM25

Now that we can chunk uploaded documents, let's store those chunks in both Pinecone (for dense retrieval) and BM25 (for sparse retrieval).

## Example: Storing Chunks in Pinecone and BM25

```python
# Assume you have already initialized Pinecone, NomicEmbeddings, and BM25Retriever

# Inside your upload endpoint, after chunking:
embeddings_list = embeddings.embed_documents(chunks)

# Upsert to Pinecone
pinecone_vectors = [(f"chunk-{i}", vector) for i, vector in enumerate(embeddings_list)]
index.upsert(vectors=pinecone_vectors)

# Update BM25 retriever (if using an in-memory list)
documents.extend(chunks)
bm25_retriever = BM25Retriever.from_texts(documents)
```

- For persistent BM25, you may want to store and reload the document list from disk or a database.
- Make sure to use unique IDs for each chunk when upserting to Pinecone.
- This step enables hybrid retrieval in the next phase.

--- 

# Phase 6: Quiz Generation Endpoint

We'll create a FastAPI endpoint that:
- Accepts a query and (optionally) a difficulty level
- Retrieves relevant, reranked, and compressed context
- Checks Redis for a cached quiz
- If not cached, calls the Groq API to generate a quiz
- Stores the generated quiz in Redis for future requests

## Example: Quiz Generation Endpoint

```python
from fastapi import Query
import requests
from retrievers import get_relevant_documents

@app.get("/generate_quiz/")
def generate_quiz(query: str = Query(...), difficulty: str = "medium"):
    # Retrieve relevant context
    retrieved_docs = get_relevant_documents(query)
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    context_hash = hash(context)
    cached = redis_client.get(f"quiz:{context_hash}")
    if cached:
        return {"quiz": cached.decode()}
    # Generate quiz using Groq API
    prompt = (
        f"Generate 5 {difficulty} questions with answers and explanations "
        f"based on the following educational content:\n{context}"
    )
    response = requests.post(
        "https://api.groq.com/v1/chat/completions",
        headers={"Authorization": f"Bearer YOUR_GROQ_API_KEY"},
        json={
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    quiz = response.json()["choices"][0]["message"]["content"]
    redis_client.set(f"quiz:{context_hash}", quiz)
    return {"quiz": quiz}
```

- Replace `YOUR_GROQ_API_KEY` with your actual API key.
- This endpoint will be the main interface for quiz generation.

--- 