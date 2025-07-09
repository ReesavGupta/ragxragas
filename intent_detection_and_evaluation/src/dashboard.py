import streamlit as st
import json
import os
import pandas as pd
import requests

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '../data/eval_results.json')
API_URL = "http://localhost:8000/rag/query"

st.set_page_config(page_title="RAG Evaluation Dashboard", layout="wide")
st.title("RAG Evaluation Dashboard")

# --- New: Query form ---
st.header("Try the RAG API")
with st.form("query_form"):
    user_query = st.text_input("Enter your question:")
    submit = st.form_submit_button("Submit")

if submit and user_query:
    with st.spinner("Querying RAG pipeline..."):
        try:
            response = requests.post(API_URL, json={"question": user_query})
            if response.status_code == 200:
                data = response.json()
                st.success(f"Intent: {data['intent']}")
                st.markdown(f"**Answer:** {data['answer']}")
            else:
                st.error(f"API Error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {e}")

# --- A/B Comparison ---
# ab_options = ["Ollama (Local)", "GROQ (Cloud)", "Both"]
# ab_choice = st.sidebar.selectbox("Select Backend for Evaluation Results", ab_options)

# Map selection to file paths
# ab_files = {
#     "Ollama (Local)": os.path.join(os.path.dirname(__file__), '../data/eval_results_ollama.json'),
#     "GROQ (Cloud)": os.path.join(os.path.dirname(__file__), '../data/eval_results_groq.json'),
# }

def load_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

data = load_results()
summary = data["summary"]
results = data["results"]
df = pd.DataFrame(results)

# Summary metrics
st.header("Summary Metrics")
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
col1.metric("Intent Accuracy", f"{summary['intent_accuracy']*100:.1f}%")
col2.metric("Avg. Response Time (s)", f"{summary['avg_response_time']:.2f}")
col3.metric("Avg. Context Utilization", f"{summary.get('avg_context_utilization', 0):.2f}")
col4.metric("Avg. Cosine Similarity", f"{summary.get('avg_cosine_similarity', 0):.2f}")
col5.metric("Avg. Token Usage", f"{summary.get('avg_token_usage', 0):.2f}")
col6.metric("Total Time (s)", f"{summary['total_time']:.2f}")
col7.metric("Total Queries", summary['total'])

# Charts
st.header("Response Time Distribution")
st.bar_chart(df['response_time'])
st.header("Context Utilization Distribution")
st.bar_chart(df['context_utilization'])
st.header("Cosine Similarity Distribution")
st.bar_chart(df['cosine_similarity'])
st.header("Token Usage Distribution")
st.bar_chart(df['token_usage'])
st.header("Intent Classification Breakdown")
intent_counts = df['true_intent'].value_counts()
intent_correct = df[df['is_correct_intent']]['true_intent'].value_counts()
intent_acc = (intent_correct / intent_counts * 100).fillna(0)
st.dataframe(pd.DataFrame({
    'Total': intent_counts,
    'Correct': intent_correct,
    'Accuracy (%)': intent_acc.round(1)
}))
# Filter/search
st.header("Browse Test Results")
intent_filter = st.selectbox("Filter by intent", options=["all"] + df['true_intent'].unique().tolist())
correct_filter = st.selectbox("Show only", options=["all", "correct", "incorrect"])
search_query = st.text_input("Search query text")
filtered = df.copy()
if intent_filter != "all":
    filtered = filtered[filtered['true_intent'] == intent_filter]
if correct_filter == "correct":
    filtered = filtered[filtered['is_correct_intent']]
elif correct_filter == "incorrect":
    filtered = filtered[~filtered['is_correct_intent']]
if search_query:
    filtered = filtered[filtered['query'].str.contains(search_query, case=False)]
st.dataframe(filtered[['id', 'query', 'true_intent', 'predicted_intent', 'is_correct_intent', 'answer', 'response_time', 'context_utilization', 'cosine_similarity', 'token_usage']]) 