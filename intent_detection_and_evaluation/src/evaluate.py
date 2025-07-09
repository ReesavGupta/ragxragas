import json
import time
import os
from src.intent.classifier import HybridIntentClassifier
from src.retrieval.retriever import IntentRAGFactory
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_SET_PATH = os.path.join(BASE_DIR, "data", "test_set.json")
RESULTS_PATH = os.path.join(BASE_DIR, "data", "eval_results.json")

load_dotenv()
# Load test set
with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
    test_set = json.load(f)

# Initialize classifier and RAG factory
intent_classifier = HybridIntentClassifier(mode="hybrid")
llm = OllamaLLM(model="gemma3:1b")
rag_factory = IntentRAGFactory(llm)

results = []
correct_intent = 0
start_time = time.time()

total = len(test_set)

for item in test_set:
    query = item["query"]
    true_intent = item["intent"]
    t0 = time.time()
    predicted_intent = intent_classifier.classify(query)
    rag_pipeline = rag_factory.get_pipeline(predicted_intent)
    answer = rag_pipeline.run(query)
    t1 = time.time()
    is_correct = (predicted_intent == true_intent)
    if is_correct:
        correct_intent += 1
    results.append({
        "id": item["id"],
        "query": query,
        "true_intent": true_intent,
        "predicted_intent": predicted_intent,
        "is_correct_intent": is_correct,
        "answer": answer,
        "response_time": t1 - t0
    })

total_time = time.time() - start_time
intent_accuracy = correct_intent / total
avg_response_time = sum(r["response_time"] for r in results) / total

summary = {
    "intent_accuracy": intent_accuracy,
    "avg_response_time": avg_response_time,
    "total_time": total_time,
    "total": total
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump({"summary": summary, "results": results}, f, indent=2)

print("Evaluation complete.")
print(json.dumps(summary, indent=2)) 