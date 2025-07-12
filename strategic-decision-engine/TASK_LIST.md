# Strategic Decision Engine - Task List

## Project Setup
- [x] Initialize repository and environment
- [x] Set up Python, requirements, Docker
- [x] Configure .env and secrets management
  - Redis and PostgreSQL containers are running via Docker

## Document Upload & Processing
- [x] Implement document upload (PDF, DOCX, XLSX, CSV, TXT)
- [x] Text extraction and chunking pipeline
- [x] Embedding generation (langchain-nomic)
- [x] Store embeddings in Pinecone (langchain-pinecone)
- [x] Store metadata in PostgreSQL

## Retrieval & RAG Pipeline
- [ ] Implement dense retrieval (Pinecone, langchain-pinecone)
- [ ] Implement sparse retrieval (BM25/Redis)
- [ ] Hybrid retrieval orchestration
- [ ] Advanced reranking (multi-model ensemble)
- [ ] Contextual compression/filtering

## Query Decomposition & Tool Calling
- [ ] Query decomposition module
- [ ] Integrate external APIs (market, financial, industry)
- [ ] LLM orchestration (langchain_groq, OpenAI, etc.)

## Citation-based Responses
- [ ] Source tracking for all answers
- [ ] Response formatting with citations

## Visualization & Dashboard
- [ ] Streamlit dashboard (MVP)
- [ ] Data visualization (charts, tables)
- [ ] User session management (Redis)

## Evaluation & RAGAS
- [ ] Integrate RAGAS evaluation framework
- [ ] Implement metrics: Faithfulness, Relevancy, Precision, Recall, Correctness
- [ ] Evaluation dashboard

## Testing & Deployment
- [ ] Unit and integration tests
- [ ] Documentation
- [ ] Dockerization and deployment scripts

---

*Check off tasks as you complete them. Add notes, blockers, and progress updates as needed.* 