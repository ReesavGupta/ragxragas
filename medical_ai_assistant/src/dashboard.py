from dotenv import load_dotenv; load_dotenv()
import streamlit as st
import requests

st.title("Medical RAG Assistant Dashboard")

API_URL = "http://localhost:8000/query"

with st.form("query_form"):
    question = st.text_input("Enter your medical question:")
    submit = st.form_submit_button("Submit")

if submit and question:
    with st.spinner("Querying RAG pipeline and evaluating..."):
        response = requests.post(API_URL, json={"question": question})
        if response.status_code == 200:
            data = response.json()
            st.subheader("Answer")
            st.write(data["answer"])
            st.subheader("RAGAS Metrics")
            st.json(data["ragas_metrics"])
            st.subheader("Latency (seconds)")
            st.write(f"{data['latency']:.2f}")
            if data["filtered"]:
                st.error(f"Filtered: {data['reason']}")
            else:
                st.success("Response passed RAGAS thresholds.")
        else:
            st.error(f"API Error: {response.status_code}")

st.header("System Metrics")
try:
    metrics_response = requests.get("http://localhost:8000/metrics")
    if metrics_response.status_code == 200:
        metrics_data = metrics_response.json()
        p95 = metrics_data.get("p95_latency")
        st.metric("p95 Latency (s)", f"{p95:.2f}" if p95 is not None else "N/A")
        if p95 is not None and p95 > 3.0:
            st.warning("p95 latency exceeds 3 seconds! Optimize your pipeline.")
    else:
        st.error(f"Failed to fetch metrics: {metrics_response.status_code}")
except Exception as e:
    st.error(f"Error fetching metrics: {e}") 