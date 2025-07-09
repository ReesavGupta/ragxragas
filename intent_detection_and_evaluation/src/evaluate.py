import json
import time
import os
from src.intent.classifier import HybridIntentClassifier
from src.retrieval.retriever import IntentRAGFactory
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
from langchain_nomic import NomicEmbeddings  # type: ignore
import numpy as np
from src.api.llm_router import LLMRouter
import typing
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_SET_PATH = os.path.join(BASE_DIR, "data", "test_set.json")
RESULTS_PATH = os.getenv("EVAL_RESULTS_PATH", os.path.join(BASE_DIR, "data", "eval_results.json"))

load_dotenv()
# Load test set
with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
    test_set = json.load(f)

# Initialize classifier and RAG factory
intent_classifier = HybridIntentClassifier(mode="hybrid")
BACKEND = os.getenv("BACKEND", "ollama").lower()
if BACKEND not in ["ollama", "groq"]:
    BACKEND = "ollama"
llm = OllamaLLM(model="gemma3:1b") if BACKEND == "ollama" else LLMRouter(backend=typing.cast(typing.Literal['ollama', 'groq'], BACKEND))
rag_factory = IntentRAGFactory(llm)

# Initialize Nomic Embeddings for relevance metric
embeddings_model = NomicEmbeddings(model="nomic-embed-text-v1.5")

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

def context_utilization(answer, context_texts):
    # Fraction of context tokens present in the answer
    context_tokens = set()
    for ctx in context_texts:
        context_tokens.update(ctx.lower().split())
    answer_tokens = set(answer.lower().split())
    if not context_tokens:
        return 0.0
    return len(context_tokens & answer_tokens) / len(context_tokens)

def count_tokens(text):
    return len(text.split())

results = []
correct_intent = 0
start_time = time.time()

context_utilization_scores = []
cosine_similarities = []
token_usages = []

total = len(test_set)

for item in test_set:
    query = item["query"]
    true_intent = item["intent"]
    t0 = time.time()
    predicted_intent = intent_classifier.classify(query)
    rag_pipeline = rag_factory.get_pipeline(predicted_intent)
    rag_result = rag_pipeline.run(query)
    answer = rag_result["answer"]
    context = rag_result["context"]
    t1 = time.time()
    is_correct = (predicted_intent == true_intent)
    if is_correct:
        correct_intent += 1
    # --- New metrics ---
    cu_score = context_utilization(answer, context)
    context_utilization_scores.append(cu_score)
    # Cosine similarity between answer and concatenated context
    context_concat = " ".join(context)
    try:
        answer_emb = embeddings_model.embed_query(answer)
        context_emb = embeddings_model.embed_query(context_concat)
        cos_sim = cosine_similarity(answer_emb, context_emb)
    except Exception:
        cos_sim = 0.0
    cosine_similarities.append(cos_sim)
    # Token usage
    token_count = count_tokens(answer)
    token_usages.append(token_count)
    results.append({
        "id": item["id"],
        "query": query,
        "true_intent": true_intent,
        "predicted_intent": predicted_intent,
        "is_correct_intent": is_correct,
        "answer": answer,
        "context": context,
        "response_time": t1 - t0,
        "context_utilization": cu_score,
        "cosine_similarity": cos_sim,
        "token_usage": token_count
    })

total_time = time.time() - start_time
intent_accuracy = correct_intent / total
avg_response_time = sum(r["response_time"] for r in results) / total
avg_context_utilization = sum(context_utilization_scores) / total
avg_cosine_similarity = sum(cosine_similarities) / total
avg_token_usage = sum(token_usages) / total

summary = {
    "intent_accuracy": intent_accuracy,
    "avg_response_time": avg_response_time,
    "avg_context_utilization": avg_context_utilization,
    "avg_cosine_similarity": avg_cosine_similarity,
    "avg_token_usage": avg_token_usage,
    "total_time": total_time,
    "total": total
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump({"summary": summary, "results": results}, f, indent=2)

print("Evaluation complete.")
print(json.dumps(summary, indent=2)) 