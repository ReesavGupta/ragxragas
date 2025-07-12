# Automated Quiz Generator

## Overview
The Automated Quiz Generator is an AI-powered system that allows instructors and learners to generate personalized quizzes from educational documents. It uses advanced retrieval, reranking, and LLM-based generation to create adaptive, high-quality assessments, all accessible through a user-friendly Streamlit interface and a robust FastAPI backend.

---

## Features
- Upload educational PDFs and automatically chunk and index them
- Hybrid retrieval (semantic + keyword) for robust context fetching
- Advanced reranking and contextual compression for relevant quiz generation
- LLM-powered quiz/question/explanation generation (Groq + LangChain)
- Adaptive difficulty based on user performance
- Fast caching and user tracking with Redis
- Simple, modern Streamlit UI for all interactions

---

## System Architecture
- **Frontend:** Streamlit web app for uploading, quiz generation, and scoring
- **Backend:** FastAPI app for document ingestion, retrieval, quiz generation, and user tracking
- **Vector Store:** Pinecone for dense semantic search
- **Sparse Retrieval:** BM25 for keyword-based search
- **Embeddings:** Nomic for high-quality vector representations
- **Reranking/Compression:** LangChain for context optimization
- **LLM:** Groq API (via LangChain) for quiz generation
- **Caching/User Data:** Redis for fast access and adaptation

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repo-url>
cd automated_quiz_generator
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root with the following (replace with your actual keys):
```
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_HOST=your-pinecone-index-host-url
NOMIC_API_KEY=your-nomic-api-key
GROQ_API_KEY=your-groq-api-key
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 4. Start Redis (if not already running)
You can use Docker:
```bash
docker run --name quiz-redis -p 6379:6379 -d redis
```

### 5. Start the FastAPI Backend
```bash
uvicorn main:app --reload
```

### 6. Start the Streamlit UI
```bash
streamlit run streamlit_app.py
```

---

## Example Usage / Workflow
1. **Upload a PDF:**
   - Use the Streamlit UI to upload an educational PDF.
2. **Generate a Quiz:**
   - Enter a topic/query and user ID, and click "Generate Quiz".
   - The system retrieves, reranks, and generates a quiz using the LLM.
   - Difficulty is auto-adjusted based on your recent scores (or you can set it manually).
3. **Submit Your Score:**
   - After taking the quiz, enter your score and submit it.
   - The system tracks your performance and adapts future quizzes.

---

## API Endpoints
- `POST /upload/` — Upload and ingest a PDF document
- `GET /generate_quiz/` — Generate a quiz for a query/topic and user (with adaptive difficulty)
- `POST /submit_score/` — Submit a user's quiz score

---

## Technologies Used
- **FastAPI** — Backend API
- **Streamlit** — User interface
- **Pinecone** — Vector database for semantic search
- **BM25** — Keyword-based retrieval
- **LangChain** — Retrieval, reranking, and LLM orchestration
- **Groq API** — LLM for quiz/question generation
- **Redis** — Caching and user performance tracking
- **Nomic** — Embeddings for semantic search

---

## Contributing & Next Steps
- Contributions are welcome! Please open issues or pull requests for improvements.
- Next steps: add tool calling for external educational APIs, richer analytics, user authentication, and more advanced UI features.

---

**This project is ready for demonstration, extension, or deployment.**
