# Automated Quiz Generator: System Design & Implementation Guide

This document outlines the architecture, technology stack, and step-by-step code examples for building an advanced, scalable assessment generation system in Python using FastAPI, Pinecone, Nomic embeddings, Groq API, Redis, and LangChain.

---

# Implementation Task List

- [x] Set up Redis client and test connection
- [x] Initialize Pinecone and Nomic embeddings
- [x] Implement BM25 sparse retriever setup
- [x] Create FastAPI endpoint for document upload and chunking
    - [x] (depends on: Redis, Pinecone/Nomic, BM25)
- [x] Implement hybrid retrieval (Pinecone + BM25) pipeline
    - [x] (depends on: Pinecone/Nomic, BM25)
- [x] Add advanced reranking and contextual compression retriever
    - [x] (depends on: Hybrid retrieval)
- [x] Integrate Redis caching for chunks and assessments
    - [x] (depends on: Redis)
- [x] Implement Groq API call for assessment generation
- [x] Create FastAPI endpoint for quiz generation
    - [x] (depends on: Reranking/compression, Groq API, Redis caching)
- [ ] Track user performance and adjust difficulty dynamically
    - [ ] (depends on: Quiz endpoint)
- [ ] Integrate tool calling for external educational APIs (optional)
- [ ] Build demo UI for instructors (optional/future)
    - [ ] (depends on: Upload/chunking, Quiz endpoint)

---

## 1. System Architecture Overview

- **Frontend**: For instructors to upload documents and review generated assessments.
- **Backend (FastAPI)**: Handles document ingestion, assessment generation, caching, and API endpoints.
- **Vector Store (Pinecone)**: Stores and retrieves dense embeddings.
- **Sparse Retrieval (BM25)**: Complements dense retrieval for hybrid search.
- **Embeddings (Nomic)**: Generates high-quality dense vectors for semantic search.
- **Reranking & Compression (LangChain)**: Improves retrieval relevance and efficiency.
- **LLM Inference (Groq API)**: Generates questions, explanations, and adapts difficulty.
- **Caching (Redis)**: Accelerates repeated queries and stores user/session data.

---

## 2. Key Implementation Components

### A. Hybrid Retrieval-Augmented Generation (RAG)
- Combine dense (Pinecone) and sparse (BM25) retrieval.
- Use LangChain retriever wrappers to merge results.

### B. Advanced Reranking with Cross-Encoder Models
- Use LangChain’s CrossEncoderReranker with Hugging Face models for reranking.
- Wrap with ContextualCompressionRetriever for further filtering.

### C. Contextual Compression with Dynamic Chunk Sizing
- Use LangChain’s contextual compression retrievers to adjust chunk sizes dynamically.

### D. Redis Caching Layer
- Cache document chunks, assessments, and user data with clear namespaces.

### E. Tool Calling & Dynamic Difficulty Adjustment
- Integrate educational APIs and use user performance data to adjust question difficulty.

---

## 3. Technology Stack & Integration

| Component         | Technology/Library         | Purpose                                   |
|-------------------|---------------------------|--------------------------------------------|
| API Framework     | FastAPI                   | RESTful endpoints, async support           |
| Dense Embeddings  | Nomic + LangChain         | High-quality vector representations        |
| Vector Store      | Pinecone                  | Scalable vector search                     |
| Sparse Retrieval  | BM25 (Whoosh)             | Keyword-based retrieval                    |
| Reranking         | LangChain (HuggingFace)   | Cross-encoder reranking, compression       |
| LLM Inference     | Groq API                  | Fast, scalable LLM completions             |
| Caching           | Redis                     | Low-latency, persistent caching            |

---

## 4. Implementation Steps & Code Examples

### Step 1: Install Required Packages
```bash
pip install fastapi uvicorn pinecone-client redis langchain langchain-nomic langchain-community whoosh sentence-transformers
```

### Step 2: Set Up Redis
```python
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

### Step 3: Set Up Pinecone & Nomic Embeddings
```python
import pinecone
from langchain_nomic import NomicEmbeddings

pinecone.init(api_key="YOUR_PINECONE_API_KEY", environment="us-west1-gcp")
index = pinecone.Index("educational-content")
embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5")
```

### Step 4: Set Up BM25 (Sparse Retrieval)
```python
from langchain_community.vectorstores import BM25Retriever

documents = ["chunk1 text", "chunk2 text", "chunk3 text", ...]
bm25_retriever = BM25Retriever.from_texts(documents)
```

### Step 5: Document Upload and Chunking (FastAPI Endpoint)
```python
from fastapi import FastAPI, File, UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = FastAPI()

@app.post("/upload/")
async def upload_doc(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode()
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = splitter.split_text(text)
    for chunk in chunks:
        vector = embeddings.embed_documents([chunk])[0]
        index.upsert([(chunk, vector)])
        documents.append(chunk)
    return {"message": f"Uploaded and indexed {len(chunks)} chunks."}
```

### Step 6: Hybrid Retrieval
```python
from langchain_community.vectorstores import PineconeRetriever
from langchain.retrievers import EnsembleRetriever

pinecone_retriever = PineconeRetriever(index=index, embedding=embeddings)
hybrid_retriever = EnsembleRetriever(retrievers=[pinecone_retriever, bm25_retriever])
```

### Step 7: Advanced Reranking & Contextual Compression
```python
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import ContextualCompressionRetriever

cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
reranker = CrossEncoderReranker(model=cross_encoder, top_n=5)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker, base_retriever=hybrid_retriever
)
```

### Step 8: Caching with Redis
```python
def cache_chunks(chunks):
    for chunk in chunks:
        redis_client.set(f"chunk:{hash(chunk)}", chunk)

def get_cached_chunk(chunk_hash):
    return redis_client.get(f"chunk:{chunk_hash}")
```

### Step 9: Assessment Generation with Groq API (Pseudo-code)
```python
import requests

def generate_questions(context, difficulty="medium"):
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
    return response.json()["choices"][0]["message"]["content"]
```

### Step 10: FastAPI Endpoint for Quiz Generation
```python
from fastapi import Query

@app.get("/generate_quiz/")
def generate_quiz(query: str = Query(...), difficulty: str = "medium"):
    retrieved_docs = compression_retriever.get_relevant_documents(query)
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    context_hash = hash(context)
    cached = get_cached_chunk(context_hash)
    if cached:
        return {"quiz": cached.decode()}
    quiz = generate_questions(context, difficulty)
    redis_client.set(f"quiz:{context_hash}", quiz)
    return {"quiz": quiz}
```

### Step 11: Dynamic Difficulty (Track User Performance)
- Store user performance in Redis and adjust the difficulty parameter in the `/generate_quiz/` endpoint accordingly.

### Step 12: Tool Calling (External APIs)
- Use LangChain's agent framework or `requests` to call external educational APIs as needed.

### Step 13: Running the API
```bash
uvicorn main:app --reload
```

---

## 5. Demo & Next Steps
- Build a demo UI for instructors to upload content and generate assessments.
- Test with real educational material to validate retrieval, generation, and caching.
- Monitor and tune caching, chunking, and reranking parameters for optimal performance. 