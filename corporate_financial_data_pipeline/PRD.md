# Corporate Financial Data RAG Pipeline – PRD

## Overview
Build a scalable, production-ready Retrieval-Augmented Generation (RAG) system for querying corporate financial documents (PDFs) using Python, LangChain, Nomic embeddings, Pinecone vector store, Redis (with RQ for background jobs and caching), and LangChain-Grok for LLM responses. The system will support concurrent queries, intelligent caching, background ingestion of new documents, and a Streamlit-based UI.

## Objectives
- Ingest and process financial PDFs (annual reports, earnings, statements).
- Store document embeddings in Pinecone using Nomic.
- Retrieve relevant document chunks for user queries.
- Generate answers using LangChain-Grok.
- Cache results in Redis with smart TTLs.
- Handle high concurrency and background processing with RQ.
- Provide a robust, async API for querying and monitoring.
- Deliver an interactive Streamlit UI for end users.

## Key Features
1. **Document Ingestion Pipeline**
   - Upload and process PDFs.
   - Chunk, embed (Nomic), and store in Pinecone.
   - Background processing with RQ.

2. **RAG Query API**
   - Async FastAPI endpoints for financial queries.
   - Retrieve relevant chunks from Pinecone.
   - Generate answers with LangChain-Grok.

3. **Caching & Rate Limiting**
   - Redis caching for query results (TTL: 1h real-time, 24h historical).
   - Rate limiting per API key.

4. **Monitoring & Metrics**
   - Real-time system metrics (requests, latency, cache hits, queue status).

5. **Load Testing**
   - Scripts for burst and performance testing.

6. **User Interface**
   - Streamlit-based UI for uploading documents and querying the system.

## Technical Stack
- **Python** (main language)
- **LangChain** (core RAG framework)
- **langchain-community** (for Nomic embeddings)
- **langchain-nomic** (Nomic integration)
- **langchain-pinecone** (Pinecone vector store)
- **Pinecone** (vector DB)
- **Redis** (caching, RQ queue)
- **RQ** (background jobs)
- **LangChain-Grok** (LLM)
- **FastAPI** (async API)
- **Streamlit** (UI)
- **PDFs** (data format)

## Stepwise Project Plan & Checklist

### 1. Project Setup
- [X] Initialize Python project structure
- [X] Set up virtual environment and requirements.txt
- [X] Configure environment variables

### 2. Data Ingestion & Processing
- [X] PDF loader and chunker (LangChain)
- [X] Nomic embeddings integration (langchain-nomic)
- [X] Pinecone vector store integration (langchain-pinecone)
- [X] Background ingestion jobs with RQ

### 3. RAG Query API
- [X] Async FastAPI setup
- [X] Query endpoint: retrieve, rerank, and answer with LangChain-Grok
- [X] LangChain-Grok integration
- [X] API key authentication and rate limiting

### 4. Caching & Redis Integration
- [X] Redis setup for caching query results
- [X] Smart TTL logic (1h/24h)
- [X] Cache versioning for updated data

### 5. Concurrency & Scaling
- [X] Async connection pooling for Redis
- [X] Async connection pooling for Pinecone
- [X] RQ worker setup for background jobs

### 6. Monitoring & Metrics
- [X] Integrate metrics collection (e.g., Prometheus, custom FastAPI endpoints)
- [X] Real-time dashboard setup

### 7. Load Testing
- [X] Write load testing scripts (e.g., Locust, k6)
- [X] Run burst and performance tests
- [X] Collect and analyze metrics

### 8. User Interface
- [X] Streamlit UI for document upload and querying

### 9. Documentation
- [ ] Write README with setup, usage, and architecture
- [ ] API documentation (Swagger/OpenAPI)

## Checklist Table

| Step | Task | Status |
|------|------|--------|
| 1    | Project structure & env setup | X |
| 2    | PDF loader & chunker | X |
| 2    | Nomic embeddings | X |
| 2    | Pinecone integration | X |
| 2    | RQ background jobs | X |
| 3    | FastAPI async API | X |
| 3    | Query endpoint (RAG) | X |
| 3    | LangChain-Grok integration | X |
| 3    | API key/rate limiting | X |
| 4    | Redis caching | X |
| 4    | Smart TTL/versioning | X |
| 4    | Cache versioning | X |
| 5    | Async connection pooling (Redis) | X |
| 5    | Async connection pooling (Pinecone) | X |
| 5    | RQ worker setup | X |
| 6    | Monitoring/metrics | X |
| 6    | Real-time dashboard | X |
| 7    | Load testing scripts | X |
| 7    | Performance validation | X |
| 8    | Streamlit UI | X |
| 9    | Documentation | ⬜️ | 