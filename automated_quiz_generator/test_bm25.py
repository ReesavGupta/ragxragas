from langchain_community.vectorstores import BM25Retriever

# Example list of document chunks (replace with your actual chunks)
documents = [
    "This is the first document chunk.",
    "Another chunk of educational content.",
    "Further information for retrieval testing."
]

bm25_retriever = BM25Retriever.from_texts(documents)

# Test retrieval
results = bm25_retriever.get_relevant_documents("educational content")
print("BM25 Retrieval Results:")
for doc in results:
    print(doc) 