from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time
import numpy as np
import json
import ast

from src.load_and_chunk.load_and_chunk import load_documents, chunk_text
from src.vector_store.embeddings_and_vectorstore import create_embeddings, initialize_vec_store_and_embedding_model
from src.retriever.retriever import build_rag_graph, State
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, FactualCorrectness, ContextPrecision, AnswerRelevancy
from ragas import EvaluationDataset, RunConfig, evaluate
from langchain import hub
from src.retriever.retriever import init_groq
from langchain_core.documents import Document
import os
from dotenv import load_dotenv; load_dotenv()
# RAGAS evaluation will be imported and integrated for filtering

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    # Optionally allow user to specify context or other params in future

class QueryResponse(BaseModel):
    answer: str
    ragas_metrics: Optional[dict] = None
    latency: float
    filtered: bool = False
    reason: Optional[str] = None

# Initialize vector store and RAG graph at startup
vector_store = initialize_vec_store_and_embedding_model()
graph = build_rag_graph(vector_store)

# Prepare LLM and prompt for RAGAS evaluation
llm = init_groq()
prompt = hub.pull("rlm/rag-prompt")
evaluator_llm = LangchainLLMWrapper(llm)
run_config = RunConfig(timeout=60)

latency_history = []
MAX_HISTORY = 1000

def record_latency(latency):
    latency_history.append(latency)
    if len(latency_history) > MAX_HISTORY:
        latency_history.pop(0)

def get_p95_latency():
    if not latency_history:
        return None
    return float(np.percentile(latency_history, 95))

def extract_relevant_text(page_content):
    # Try to parse as JSON
    data = None
    if isinstance(page_content, str):
        try:
            data = json.loads(page_content)
        except Exception:
            try:
                data = ast.literal_eval(page_content)
            except Exception:
                data = None
    if data is None:
        # Fallback: return a truncated/cleaned string
        return page_content[:200] + "..." if len(page_content) > 200 else page_content

    # If it's a dict, extract key fields
    if isinstance(data, dict):
        effect = ""
        if "reaction" in data and isinstance(data["reaction"], list) and data["reaction"]:
            effect = data["reaction"][0].get("reactionmeddrapt", "")
        drug = ""
        if "drug" in data and isinstance(data["drug"], list) and data["drug"]:
            drug = data["drug"][0].get("medicinalproduct", "")
        indication = data["drug"][0].get("drugindication", "") if "drug" in data and isinstance(data["drug"], list) and data["drug"] else ""
        return f"Drug: {drug}, Indication: {indication}, Adverse Effect: {effect}"
    return str(data)

def llm_extract_relevant_text(llm, page_content):
    prompt = (
        "Extract all side effects (as listed in the text) and drug names from the following medical record. "
        "List each side effect and drug name exactly as found, separated by commas. "
        "If none are found, return 'None'.\n\n"
        f"{page_content}\n\n"
        "Side Effects and Drug Names:"
    )
    try:
        result = llm.invoke(prompt)
        return result.content.strip()
    except Exception as e:
        return extract_relevant_text(page_content)

@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    start_time = time.time()
    initial_state: State = {
        "question": request.question,
        "context": [],
        "answer": ""
    }
    result = graph.invoke(initial_state)
    answer = result["answer"]
    context_docs = result.get("context", [])
    latency = time.time() - start_time
    record_latency(latency)

    # Prepare RAGAS evaluation input
    if context_docs and isinstance(context_docs[0], Document):
        context_texts = [llm_extract_relevant_text(llm, doc.page_content) for doc in context_docs]
    else:
        context_texts = []

    golden_dataset = [
        {
            "user_input": request.question,
            "response": answer,
            "retrieved_contexts": context_texts,
            "reference": None  # No reference for live queries
        }
    ]
    evaluation_dataset = EvaluationDataset.from_list(golden_dataset)
    metrics = [
        Faithfulness(),
        AnswerRelevancy(),
    ]
    result_metrics = evaluate(
        dataset=evaluation_dataset,
        metrics=metrics,
        llm=evaluator_llm,
        run_config=run_config
    )
    # result_metrics is a list of dicts or has a .results attribute
    try:
        # Try to convert result_metrics to a dict using to_pandas if available
        if hasattr(result_metrics, 'to_pandas'):
            metrics_dict = result_metrics.to_pandas().iloc[0].to_dict()
        else:
            metrics_dict = {}
    except Exception as e:
        metrics_dict = {}
        reason = f"RAGAS evaluation failed: {str(e)}"
    faithfulness = metrics_dict.get("faithfulness", 0)
    context_precision = metrics_dict.get("context_precision", 0)

    filtered = False
    reason = None
    if faithfulness < 0.90 or context_precision < 0.85:
        filtered = True
        reason = f"Response filtered: Faithfulness={faithfulness:.2f}, Context Precision={context_precision:.2f}"

    return QueryResponse(
        answer=answer,
        ragas_metrics=metrics_dict,
        latency=latency,
        filtered=filtered,
        reason=reason
    )

@app.get("/metrics")
def metrics():
    p95 = get_p95_latency()
    return {"p95_latency": p95, "history_size": len(latency_history)} 