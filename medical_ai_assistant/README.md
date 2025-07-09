# Medical AI Assistant

A production-ready Medical Knowledge Assistant RAG pipeline for healthcare professionals to query medical literature, drug interactions, and clinical guidelines using OpenAI API, with comprehensive RAGAS evaluation and real-time monitoring.

---

## Requirements

### Core System
- **RAG Pipeline:** Medical document ingestion → Vector DB → Retrieval → OpenAI generation
- **Data Sources:** Medical PDFs, drug databases, clinical protocols
- **API:** RESTful endpoints for medical queries

### RAGAS Implementation
- **Core Metrics:** Context Precision, Context Recall, Faithfulness, Answer Relevancy
- **Medical Evaluation:** Custom datasets with medical Q&A pairs
- **Automated Pipeline:** Batch evaluation and real-time monitoring
- **Quality Thresholds:** Faithfulness > 0.90, Context Precision > 0.85

### Production Features
- **Monitoring Dashboard:** Real-time RAGAS metrics tracking
- **Safety System:** RAGAS-validated response filtering
- **Performance:** Response latency p95 < 3 seconds
- **Deployment:** Dockerized API with RAGAS monitoring

---

## Deliverables
- Complete RAG system with medical document processing
- RAGAS evaluation framework with all core metrics
- Production API with real-time RAGAS monitoring
- Demo showing query → retrieval → generation → RAGAS evaluation

---

## Success Criteria
- Faithfulness > 0.90 (medical accuracy)
- Context Precision > 0.85
- Zero harmful medical advice
- Working RAGAS monitoring system

---

## Why Only Faithfulness and Context Precision in Live Evaluation?

In live (production) settings, we **cannot provide a reference (ground truth answer)** for each user query. Metrics like `context_recall` and `answer_relevancy` require a reference answer, which is only available in offline or batch evaluation with annotated datasets. 

**Therefore, for real-time/live queries, we use only:**
- **Faithfulness:** Measures if the answer is grounded in the retrieved context (medical accuracy).
- **Context Precision:** Measures if the retrieved context is relevant and useful for the answer.

This ensures that the system is both accurate and safe, even without ground truth answers.

---

## Notes on Performance
- The system currently takes several seconds per query (p95 latency > 3s), mainly due to LLM-based context extraction and RAGAS evaluation. Further optimization is possible.

---

## Example Results

**Query → Retrieval → Generation → RAGAS Evaluation:**

![Result Example 1](PLACEHOLDER_IMAGE_1.png)

![Result Example 2](PLACEHOLDER_IMAGE_2.png)

---

## Goal

Build a production-ready medical RAG system that uses RAGAS to ensure accurate, safe responses.

---

## How to Run

1. Install dependencies:
   ```bash
   pip install -r medical_ai_assistant/requirements.txt
   ```
2. Start the API:
   ```bash
   cd medical_ai_assistant
   uvicorn src.api:app --reload
   ```
3. Run the dashboard:
   ```bash
   streamlit run src/dashboard.py
   ```
4. (Optional) Run the demo:
   ```bash
   python demo.py
   ```

---

## Folder Structure

```
medical_ai_assistant/
│
├── data/                  # Medical datasets, drug-event JSON, etc.
├── src/                   # Main source code for the RAG pipeline
│   ├── api.py             # FastAPI backend (main API server)
│   ├── dashboard.py       # Streamlit dashboard for real-time monitoring
│   ├── main.py            # Script for running the full pipeline end-to-end
│   ├── load_and_chunk/    # Document loading and chunking utilities
│   ├── retriever/         # Retrieval logic and RAG graph definition
│   ├── vector_store/      # Embedding and vector store setup (Pinecone, etc.)
│   └── ragas/             # RAGAS evaluation and test data utilities
│
├── demo.py                # Demo script for sample queries and metrics
├── requirements.txt       # Python dependencies
├── Dockerfile             # Containerization for API and dashboard
├── .env                   # Environment variables (API keys, config)
└── README.md              # Project documentation (this file)
```

- **data/**: Place your medical datasets, drug-event files, etc. here.
- **src/**: All core code for the RAG pipeline, API, dashboard, and evaluation.
- **demo.py**: Run a sample query and print results in the terminal.
- **requirements.txt**: All Python dependencies for the project.
- **Dockerfile**: Build and run the API and dashboard in a single container.
- **.env**: Store your API keys and environment variables (never commit secrets!).

---

## Dockerfile & Container Usage

The provided `Dockerfile` allows you to run both the FastAPI backend and the Streamlit dashboard in a single container for easy deployment and demoing.

**Key features:**
- Based on `python:3.10-slim` for a lightweight image.
- Installs all dependencies from `requirements.txt`.
- Copies all code and the `.env` file into the container.
- Exposes ports `8000` (API) and `8501` (dashboard).
- Default command runs both the API and dashboard together (for development/demo).

**How to build and run:**

```bash
# From the project root
cd medical_ai_assistant

docker build -t medical-ai-assistant .

docker run -p 8000:8000 -p 8501:8501 --env-file .env medical-ai-assistant
```

- The API will be available at [http://localhost:8000](http://localhost:8000)
- The dashboard will be available at [http://localhost:8501](http://localhost:8501)

**Note:** For production, you may want to run the API and dashboard as separate services, use a process manager, or add HTTPS/reverse proxying as needed.

---

## License

MIT 