import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
from langchain_nomic import NomicEmbeddings  # type: ignore

load_dotenv()

# Map each intent to its PDF and Pinecone index
INTENT_CONFIG = {
    "technical_support": {
        "pdf": "data/technical-support.pdf",
        "index": os.getenv("PINECONE_TECH_SUPPORT_INDEX", "tech-support-index"),
    },
    "billing_account": {
        "pdf": "data/billing-and-accounts.pdf",
        "index": os.getenv("PINECONE_BILLING_INDEX", "billing-index"),
    },
    "feature_request": {
        "pdf": "data/feature-requests.pdf",
        "index": os.getenv("PINECONE_FEATURE_INDEX", "feature-index"),
    },
}

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in environment.")

pc = Pinecone(api_key=PINECONE_API_KEY)

# Chunking config
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

def ingest_intent(intent: str):
    """
    Ingest the PDF for a given intent into its Pinecone index.
    """
    config = INTENT_CONFIG[intent]
    print(f"Ingesting {config['pdf']} into index {config['index']} with NomicEmbeddings (nomic-embed-text-v1.5)")
    loader = PyPDFLoader(config["pdf"])
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs)
    nomic_api_key = os.getenv("NOMIC_API_KEY")
    embeddings = NomicEmbeddings(nomic_api_key=nomic_api_key, model="nomic-embed-text-v1.5")
    index = pc.Index(config["index"])
    vector_store = PineconeVectorStore(embedding=embeddings, index=index)
    # PineconeVectorStore.add_documents expects a list of Document objects
    for i in range(0, len(chunks), 50):
        batch = chunks[i:i+50]
        vector_store.add_documents(documents=batch)
    print(f"Ingested {len(chunks)} chunks for {intent}.")

if __name__ == "__main__":
    for intent in INTENT_CONFIG:
        ingest_intent(intent)
    print("Ingestion complete.") 