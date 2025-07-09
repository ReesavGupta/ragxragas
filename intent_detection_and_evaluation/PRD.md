# Product Requirements Document (PRD)

## Project: Local RAG Pipeline with Intent Detection and Evaluation

### Background
Build a customer support system for a SaaS company that handles different query types (technical issues, billing questions, feature requests) with tailored processing strategies.

---

## Goals
- Provide accurate, context-aware responses to customer queries.
- Route queries to the correct intent (Technical Support, Billing/Account, Feature Requests).
- Support both local LLM (Ollama/Llama) and GROQ API with fallback and A/B testing.
- Evaluate system performance with clear metrics and dashboard.
- Enable streaming for long responses and provide a simple web UI for testing.

---

## Requirements

### 1. Local LLM Setup
- [ ] Set up Ollama for local LLM inference.
- [ ] Create an API wrapper that can switch between local Llama and GROQ (fallback mechanism).
- [ ] Implement request queuing to handle concurrent requests efficiently.

### 2. Intent Detection System
- [ ] Build a classifier for three categories:
    - Technical Support (routes to code examples, documentation)
    - Billing/Account (routes to pricing tables, policies)
    - Feature Requests (routes to roadmap, comparison data)
- [ ] Use different prompt templates and retrieval strategies for each intent.

### 3. Evaluation Framework
- [ ] Prepare a test set: 20 queries per intent (60 total).
- [ ] Implement metrics:
    - Intent classification accuracy
    - Response relevance (cosine similarity)
    - Context utilization score
    - Response time and token usage
- [ ] Build a dashboard for metric visualization.

### 4. Deliverables
- [ ] Working codebase (Python, using FastAPI, LangChain, LangGraph, Streamlit, Groq API, etc.)
- [ ] Evaluation report with metrics.
- [ ] README with setup instructions.
- [ ] Sample test queries and expected outputs.
- [ ] A/B testing between local Llama and GROQ.
- [ ] Streaming support for long responses.
- [ ] Simple web UI for testing.

---

## Architecture Overview
- **API Layer:** FastAPI for serving requests, managing LLM switching, and streaming.
- **Intent Detection:** Classifier (could use simple ML, zero-shot, or embedding-based) to route queries.
- **Retrieval:** LangChain/LangGraph for RAG, with intent-specific prompt templates and retrieval chains.
- **Evaluation:** Scripts and dashboard (Streamlit) for metrics and A/B testing.
- **UI:** Streamlit web app for manual testing and demo.

---

## Inspiration
- Leverage RAG and RAGAS patterns from `medical_ai_assistant` for chunking, retrieval, and evaluation.

---

## Timeline & Milestones
1. Project scaffolding and LLM setup
2. Intent detection and routing
3. Retrieval and prompt engineering
4. Evaluation framework and dashboard
5. UI and streaming
6. Final testing and documentation

---

## Notes
- Use `.env` for API keys and configuration.
- Modularize code for easy extension and testing.
- Ensure reproducibility and clear instructions in README.

---

## References
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [RAGAS](https://github.com/explodinggradients/ragas)
- [Ollama](https://ollama.com/)
- [Streamlit](https://streamlit.io/) 