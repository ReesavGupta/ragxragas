import os
from langchain_pinecone import PineconeVectorStore
from langchain_nomic import NomicEmbeddings
from pinecone import Pinecone
from langchain_core.documents import Document

def initialize_vec_store_and_embedding_model():
    index_name = os.getenv("PINECONE_INDEX")
    api_key = os.getenv("PINECONE_API_KEY")
    nomic_api_key = os.getenv("NOMIC_API_KEY")
    if not api_key:
        raise ValueError("Missing PINECONE_API_KEY in environment.")
    if not index_name:
        raise ValueError("Missing PINECONE_INDEX in environment.")

    embeddings = NomicEmbeddings( nomic_api_key=nomic_api_key ,model="nomic-embed-text-v1.5")

    try:
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Pinecone index: {e}")

    return PineconeVectorStore(embedding=embeddings, index=index)

def create_embeddings(chunks: list[Document]):
    if not all(isinstance(doc, Document) for doc in chunks):
        raise TypeError("All chunks must be of type Document")

    vector_store = initialize_vec_store_and_embedding_model()
    
    for i in range(0, len(chunks), 50):
        batch = chunks[i:i+50]
        vector_store.add_documents(documents=batch)
