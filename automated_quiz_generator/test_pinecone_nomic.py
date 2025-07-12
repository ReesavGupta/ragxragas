import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_nomic import NomicEmbeddings

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_HOST=  os.getenv("PINECONE_INDEX_HOST")
NOMIC_API_KEY = os.getenv("NOMIC_API_KEY")
INDEX_NAME = "quiz-index"   

try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if INDEX_NAME and PINECONE_INDEX_HOST:
        index = pc.Index(INDEX_NAME, host=PINECONE_INDEX_HOST)
        print(f"Connected to Pinecone index: {INDEX_NAME}")
    else:
        print(f"something went wrong while connecting to pinecone")
except Exception as e:
    print(f"Failed to connect to Pinecone: {e}")

try:
    embeddings = NomicEmbeddings(nomic_api_key=NOMIC_API_KEY ,model="nomic-embed-text-v1.5")
    vector = embeddings.embed_documents(["Sample text"])[0]
    print("Nomic embeddings initialized and test vector generated.")
except Exception as e:
    print(f"Failed to initialize Nomic embeddings: {e}") 