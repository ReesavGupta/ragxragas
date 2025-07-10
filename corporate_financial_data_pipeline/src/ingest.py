import os
from glob import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nomic import NomicEmbeddings  # type: ignore
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "data")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
NOMIC_API_KEY = os.getenv("NOMIC_API_KEY")

if not PINECONE_API_KEY or not PINECONE_INDEX_NAME or not NOMIC_API_KEY:
    raise ValueError("Missing one or more required environment variables: PINECONE_API_KEY, PINECONE_INDEX_NAME, NOMIC_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


def ingest_pdfs():
    pdf_files = glob(os.path.join(DATA_DIR, "*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {DATA_DIR}")
        return
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    embeddings = NomicEmbeddings(nomic_api_key=NOMIC_API_KEY, model="nomic-embed-text-v1.5")
    index = pc.Index(PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(embedding=embeddings, index=index)
    for pdf_path in pdf_files:
        print(f"Ingesting {pdf_path} into index {PINECONE_INDEX_NAME}")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        for i in range(0, len(chunks), 50):
            batch = chunks[i:i+50]
            vector_store.add_documents(documents=batch)
        print(f"Ingested {len(chunks)} chunks from {os.path.basename(pdf_path)}.")

if __name__ == "__main__":
    ingest_pdfs()
    print("Ingestion complete.") 