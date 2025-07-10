import streamlit as st
import requests
import os

st.set_page_config(page_title="Financial RAG Assistant", layout="centered")
st.title("📊 Financial RAG Assistant")

st.markdown("---")

# PDF Upload (for demonstration; actual ingestion is backend)
st.header("Upload Financial PDFs")
uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)
if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) selected. Please place them in the backend data directory for ingestion.")
else:
    st.info("No files selected.")

st.markdown("---")

# Query Section
st.header("Ask a Financial Question")
api_url = st.text_input("API URL", value=os.getenv("API_URL", "http://localhost:8000/query"))
api_key = st.text_input("API Key", type="password")
query = st.text_area("Your question", height=80)

if st.button("Submit Query"):
    if not api_key or not query:
        st.error("Please enter both an API key and a question.")
    else:
        with st.spinner("Querying RAG system..."):
            try:
                response = requests.post(api_url, json={"query": query, "api_key": api_key}, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    st.success("Answer:")
                    st.write(data.get("answer", "No answer returned."))
                    st.markdown("**Context:**")
                    for i, ctx in enumerate(data.get("context", [])):
                        st.code(ctx, language="markdown")
                    st.markdown(f"**Cache:** {'Hit' if data.get('cached') else 'Miss'} | **Query Type:** {data.get('query_type', 'N/A')}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

st.markdown("---")
st.caption("Minimalist UI for Financial RAG System · Powered by Streamlit") 