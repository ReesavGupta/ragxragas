import os
from typing import List, Dict, Any
from langchain_nomic import NomicEmbeddings
from pinecone import Pinecone

# Environment variables
NOMIC_API_KEY = os.getenv('NOMIC_API_KEY')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text-v1.5')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
PINECONE_INDEX = os.getenv('PINECONE_INDEX')
PINECONE_INDEX_HOST = os.getenv('PINECONE_INDEX_HOST')

if not PINECONE_INDEX and not PINECONE_INDEX_HOST:
    print("no pinecone index and host")
    
# Initialize Pinecone and Nomic embeddings at the module level, but only if required env vars are present

if PINECONE_API_KEY and PINECONE_INDEX and PINECONE_INDEX_HOST:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(name=str(PINECONE_INDEX), host=str(PINECONE_INDEX_HOST))
else:
    print("Pinecone API key, index, or host not set. Pinecone will not be initialized.")

if NOMIC_API_KEY and EMBEDDING_MODEL:
    embeddings = NomicEmbeddings(nomic_api_key=NOMIC_API_KEY, model=EMBEDDING_MODEL)
else:
    print("Nomic API key or embedding model not set. Embeddings will not be initialized.")


def upsert_embeddings(
    embeddings: List[List[float]],
    metadatas: List[Dict[str, Any]],
    namespace: str = "default"
):
    """
    Upsert a batch of embeddings and their metadata into Pinecone.
    Each embedding should have a unique 'id' in its metadata.
    """
    if len(embeddings) != len(metadatas):
        raise ValueError("Embeddings and metadatas must have the same length.")
    vectors = []
    for i, (embedding, metadata) in enumerate(zip(embeddings, metadatas)):
        if 'id' not in metadata:
            raise ValueError("Each metadata dict must contain a unique 'id' key.")
        vectors.append((metadata['id'], embedding, metadata))
    index.upsert(vectors=vectors, namespace=namespace) 


def query_pinecone(query: str, top_k: int = 5, namespace: str = "default") -> list[dict]:
    """
    Query Pinecone for top-k relevant chunks given a query string.
    Returns a list of dicts with metadata and scores.
    """
    # Embed the query using the existing embeddings object
    query_embedding = embeddings.embed_query(query)
    # Query Pinecone using the correct argument for the Pinecone client
    results = index.query(queries=[query_embedding], top_k=top_k, include_metadata=True, namespace=namespace)
    # Safely convert to dict for linter compatibility
    try:
        results_dict = results.to_dict()  # type: ignore[attr-defined]
    except AttributeError:
        results_dict = results  # type: ignore[assignment]
    matches = results_dict['matches'][0] if 'matches' in results_dict and results_dict['matches'] else []  # type: ignore[index]
    return [
        {
            'id': match['id'],
            'score': match['score'],
            'metadata': match.get('metadata', {})
        }
        for match in matches
    ] 