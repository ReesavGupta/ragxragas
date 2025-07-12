import os
from langchain_community.retrievers import BM25Retriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.vectorstores import PineconeRetriever
from langchain.retrievers import EnsembleRetriever
from langchain_nomic import NomicEmbeddings
from pinecone import Pinecone
import dotenv

dotenv.load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
NOMIC_API_KEY = os.getenv("NOMIC_API_KEY")
INDEX_NAME = "quiz-index"
INDEX_HOST = os.getenv("PINECONE_INDEX_HOST")

# Initialize Pinecone and Nomic
pc = Pinecone(api_key=PINECONE_API_KEY)
if INDEX_HOST:
    index = pc.Index(INDEX_NAME, host=INDEX_HOST)
else:
    index = None
embeddings = NomicEmbeddings(nomic_api_key=NOMIC_API_KEY, model="nomic-embed-text-v1.5")

documents = []  # Global list for BM25
bm25_retriever = None

# Advanced reranking and contextual compression setup
cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
reranker = CrossEncoderReranker(model=cross_encoder, top_n=5)

# Hybrid retriever and compression retriever
hybrid_retriever = None
compression_retriever = None

def update_bm25(chunks):
    global documents, bm25_retriever
    documents.extend(chunks)
    if documents:
        bm25_retriever = BM25Retriever.from_texts(documents)
        update_hybrid()

def update_hybrid():
    global hybrid_retriever, compression_retriever
    retrievers = []
    if index:
        pinecone_retriever = PineconeRetriever(index=index, embedding=embeddings)
        retrievers.append(pinecone_retriever)
    if bm25_retriever:
        retrievers.append(bm25_retriever)
    if retrievers:
        weights = [1.0] * len(retrievers)
        hybrid_retriever = EnsembleRetriever(retrievers=retrievers, weights=weights)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=reranker, base_retriever=hybrid_retriever
        )
    else:
        hybrid_retriever = None
        compression_retriever = None

def get_relevant_documents(query: str):
    if compression_retriever:
        return compression_retriever.get_relevant_documents(query)
    return []

def get_embeddings():
    return embeddings

def get_index():
    return index 