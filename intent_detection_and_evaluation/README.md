# Project Structure

This project is organized for modularity and clarity, inspired by RAG and RAGAS patterns. The main components are:

```
intent_detection_and_evaluation/
│
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── llm_router.py         # API wrapper for Ollama (gemma3:1b) and GROQ
│   ├── intent/
│   │   ├── __init__.py
│   │   └── classifier.py         # Intent detection logic
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── retriever.py          # Retrieval logic (prompt templates, chains)
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── metrics.py            # Evaluation metrics and utilities
│   ├── ui/
│   │   ├── __init__.py
│   │   └── app.py                # Streamlit web UI
│   └── main.py                   # FastAPI entrypoint
│
├── data/
│   ├── test_queries.json         # Test queries for evaluation
│   └── ...
│
├── requirements.txt
├── PRD.md
└── README.md
```

- **src/api/llm_router.py**: Handles switching between local Ollama (gemma3:1b) and GROQ using langchain-ollama and langchain-groq.
- **src/intent/classifier.py**: Intent detection logic (ML/embedding/zero-shot).
- **src/retrieval/retriever.py**: Retrieval-augmented generation logic, prompt templates, chains.
- **src/evaluation/metrics.py**: Evaluation metrics (accuracy, relevance, context utilization, etc.).
- **src/ui/app.py**: Streamlit web UI for testing and dashboard.
- **src/main.py**: FastAPI app for API endpoints and streaming.
- **data/**: Test queries and any static data.

This structure supports modular development and easy extension for future features. 