from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.api.llm_router import LLMRouter
from src.api.queue import enqueue_llm_request, get_llm_result
from src.intent.classifier import HybridIntentClassifier
from src.retrieval.retriever import IntentRAGFactory
from langchain_ollama import OllamaLLM

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class LLMRequest(BaseModel):
    question: str
    backend: str = "ollama"  # or "groq"

# Shared router and classifier instances
llm_router = LLMRouter()
intent_classifier = HybridIntentClassifier(mode="hybrid")
llm = OllamaLLM(model="gemma3:1b")
rag_factory = IntentRAGFactory(llm)

@app.post("/llm/request")
def enqueue_request(req: LLMRequest):
    """
    Classify intent, enqueue an LLM request. Returns a job_id and detected intent.
    """
    intent = intent_classifier.classify(req.question)
    # Pass intent as a kwarg for downstream use (retrieval, prompt, etc.)
    job_id = enqueue_llm_request(llm_router.generate, question=req.question, backend=req.backend, intent=intent)
    return {"job_id": job_id, "intent": intent}

@app.get("/llm/result/{job_id}")
def get_result(job_id: str):
    """
    Fetch the result of a queued LLM request by job_id.
    Returns result if finished, or status if still processing.
    """
    result = get_llm_result(job_id)
    if result is not None:
        return {"result": result}
    return {"status": "processing"}

class RAGRequest(BaseModel):
    question: str

@app.post("/rag/query")
def rag_query(req: RAGRequest):
    """
    Classify intent, run RAG pipeline for the detected intent, and return the answer.
    """
    intent = intent_classifier.classify(req.question)
    rag_pipeline = rag_factory.get_pipeline(intent)
    answer = rag_pipeline.run(req.question)
    return {"intent": intent, "answer": answer} 