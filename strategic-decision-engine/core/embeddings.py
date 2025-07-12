from typing import List
from langchain_nomic import NomicEmbeddings
import os

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
NOMIC_API_KEY = os.getenv('NOMIC_API_KEY')
# Initialize NomicEmbeddings (API key should be set in environment)
_nomic = None

def get_nomic():
    """
    Initialize and return a NomicEmbeddings instance using the API key and model from the environment.
    Raises ValueError if the API key or model is missing.
    """
    global _nomic
    if _nomic is None:
        if not NOMIC_API_KEY:
            raise ValueError('NOMIC_API_KEY environment variable is not set.')
        if not EMBEDDING_MODEL:
            raise ValueError('EMBEDDING_MODEL environment variable is not set.')
        _nomic = NomicEmbeddings(nomic_api_key=NOMIC_API_KEY, model=EMBEDDING_MODEL)
    return _nomic

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks using Nomic.
    Args:
        chunks (List[str]): List of text chunks to embed.
    Returns:
        List[List[float]]: List of embedding vectors.
    Raises:
        ValueError: If embedding fails or input is invalid.
    """
    nomic = get_nomic()
    if not nomic:
        raise ValueError('NomicEmbeddings instance could not be initialized.')
    if not chunks:
        return []
    try:
        return nomic.embed_documents(chunks)
    except Exception as e:
        raise ValueError(f'Embedding generation failed: {e}') 