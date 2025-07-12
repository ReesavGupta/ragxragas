# Strategic Decision Engine

A comprehensive AI-powered strategic planning platform for CEOs and business leaders.

## Features
- Document upload & processing (PDF, DOCX, XLSX, CSV, TXT)
- Hybrid RAG (dense + sparse retrieval, reranking)
- Query decomposition & tool calling
- Citation-based, explainable responses
- Data visualization (charts, tables)
- RAGAS evaluation framework

## Tech Stack
- FastAPI (backend)
- Streamlit (frontend)
- PostgreSQL/MongoDB (metadata)
- Pinecone (vector DB)
- Redis (caching)
- Langchain, RAGAS, Groq, OpenAI

## Setup
1. **Clone the repo & create a virtual environment**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Copy and configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your keys and DB info
   ```
4. **Start Redis (Docker):**
   ```bash
   docker run -d --name redis -p 6379:6379 redis:latest
   ```
5. **Run backend (FastAPI):**
   ```bash
   uvicorn backend.main:app --reload
   ```
6. **Run frontend (Streamlit):**
   ```bash
   streamlit run frontend/app.py
   ```

## Docker
- (Optional) Build and run the app in a container (see Dockerfile)

## Folder Structure
- `backend/` - FastAPI app, business logic
- `frontend/` - Streamlit dashboard
- `core/` - Document processing, RAG, LLM orchestration

## Contributing
- See TASK_LIST.md for progress and open tasks.

---
*Inspired by state-of-the-art RAG, business intelligence, and LLM orchestration best practices.* 