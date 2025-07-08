from load_and_chunk.load_and_chunk import load_documents, chunk_text 
from vector_store.embeddings_and_vectorstore import create_embeddings, initialize_vec_store_and_embedding_model
from retriever.retriever import build_rag_graph,State

import os
from dotenv import load_dotenv

def main():
    load_dotenv()

    # Step 1: Load + chunk
    documents = load_documents("data/drug-event.json")
    chunks = chunk_text(documents=documents)

    # Step 2: Create vector store and upload embeddings
    create_embeddings(chunks)
    vector_store = initialize_vec_store_and_embedding_model()

    # Step 4: Build and invoke RAG
    graph = build_rag_graph(vector_store)

    initial_state: State = {
        "question": "What adverse events are associated with VENETOCLAX?",
        "context": [],  # required key, empty list
        "answer": ""    # required key, empty string
    }

    result = graph.invoke(initial_state)

    print("🧠 Answer:", result["answer"])

if __name__ == "__main__":
    main()