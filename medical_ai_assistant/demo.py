import requests
import time
from dotenv import load_dotenv; load_dotenv()

API_URL = "http://localhost:8000/query"
METRICS_URL = "http://localhost:8000/metrics"

sample_question = "What adverse effect was reported for VENETOCLAX used in Acute myeloid leukaemia?"

print("\n--- Medical AI Assistant Demo ---\n")
print(f"Sending sample query: {sample_question}\n")

start = time.time()
response = requests.post(API_URL, json={"question": sample_question})
end = time.time()

if response.status_code == 200:
    data = response.json()
    print("Answer:")
    print(data["answer"])
    print("\nRAGAS Metrics:")
    for k, v in data["ragas_metrics"].items():
        print(f"  {k}: {v}")
    print(f"\nLatency (seconds): {data['latency']:.2f}")
    if data["filtered"]:
        print(f"\n[WARNING] Response filtered: {data['reason']}")
    else:
        print("\nResponse passed RAGAS thresholds.")
else:
    print(f"API Error: {response.status_code}")

# Show p95 latency
try:
    metrics_response = requests.get(METRICS_URL)
    if metrics_response.status_code == 200:
        metrics_data = metrics_response.json()
        p95 = metrics_data.get("p95_latency")
        print(f"\np95 Latency (s): {p95:.2f}" if p95 is not None else "p95 Latency: N/A")
    else:
        print(f"Failed to fetch metrics: {metrics_response.status_code}")
except Exception as e:
    print(f"Error fetching metrics: {e}")

print("\n---\nTo try the interactive dashboard, run: streamlit run medical_ai_assistant/src/dashboard.py\n") 