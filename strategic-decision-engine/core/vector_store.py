import os
from typing import List, Dict, Any
from langchain_nomic import NomicEmbeddings
from pinecone import Pinecone
from langchain_community.retrievers import BM25Retriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.schema import Document

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


def get_bm25_retriever(redis_client) -> BM25Retriever:
    """
    Load all chunk texts from Redis and build a BM25Retriever.
    """
    chunk_ids = redis_client.smembers("all_chunk_ids")
    chunk_ids = [cid.decode() if isinstance(cid, bytes) else cid for cid in chunk_ids]
    chunk_texts = []
    for cid in chunk_ids:
        text = redis_client.get(f"chunk:{cid}:text")
        if text is not None:
            chunk_texts.append(text.decode() if isinstance(text, bytes) else text)
    if not chunk_texts:
        raise ValueError("No chunk texts found in Redis.")
    return BM25Retriever.from_texts(chunk_texts) 


def hybrid_retrieve(query: str, top_k: int, redis_client) -> list[dict]:
    """
    Perform hybrid retrieval: combine dense (Pinecone) and sparse (BM25/Redis) results.
    Returns merged, deduplicated results with averaged scores.
    """
    # Dense retrieval
    dense_results = query_pinecone(query, top_k=top_k)
    dense_map = {r['id']: r for r in dense_results}
    # Sparse retrieval
    bm25_retriever = get_bm25_retriever(redis_client)
    sparse_docs = bm25_retriever.get_relevant_documents(query)[:top_k]
    # Map chunk texts to chunk IDs
    chunk_ids = redis_client.smembers("all_chunk_ids")  # type: ignore
    chunk_ids = [cid.decode() if isinstance(cid, bytes) else cid for cid in chunk_ids]  # type: ignore
    id_to_text = {redis_client.get(f"chunk:{cid}:text").decode(): cid for cid in chunk_ids}  # type: ignore
    sparse_map = {}
    for doc in sparse_docs:
        chunk_text = doc.page_content
        chunk_id = id_to_text.get(chunk_text)
        if chunk_id:
            sparse_map[chunk_id] = {
                'id': chunk_id,
                'content': chunk_text,
                'sparse_score': doc.metadata.get('score', 1.0)  # BM25Retriever may not provide score
            }
    # Merge results
    merged = {}
    for chunk_id, dense in dense_map.items():
        merged[chunk_id] = {
            'id': chunk_id,
            'dense_score': dense['score'],
            'sparse_score': sparse_map.get(chunk_id, {}).get('sparse_score', 0.0),
            'content': None,  # to be filled below
            'metadata': dense.get('metadata', {})
        }
    for chunk_id, sparse in sparse_map.items():
        if chunk_id not in merged:
            merged[chunk_id] = {
                'id': chunk_id,
                'dense_score': 0.0,
                'sparse_score': sparse['sparse_score'],
                'content': sparse['content'],
                'metadata': {}
            }
    # Compute average score and fill content if missing
    for chunk_id, entry in merged.items():
        entry['score'] = (entry['dense_score'] + entry['sparse_score']) / 2
        if not entry['content']:
            # Try to get content from Redis
            text = redis_client.get(f"chunk:{chunk_id}:text")
            if text:
                entry['content'] = text.decode() if isinstance(text, bytes) else text
    # Sort by combined score
    results = sorted(merged.values(), key=lambda x: x['score'], reverse=True)[:top_k]
    return results 


# Initialize cross-encoder reranker
cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
reranker = CrossEncoderReranker(model=cross_encoder, top_n=10)

def rerank_results(query: str, results: list[dict], top_k: int = 5) -> list[dict]:
    """
    Rerank a list of results (with 'content') using a cross-encoder reranker.
    Returns the reranked list with 'rerank_score', sorted by this score.
    """
    # Prepare documents for reranker
    docs = [Document(page_content=entry['content']) for entry in results]
    reranked_docs = reranker.compress_documents(docs, query)
    # Map reranked docs back to original entries
    content_to_score = {doc.page_content: doc.metadata.get('relevance_score', 0.0) for doc in reranked_docs}
    for entry in results:
        entry['rerank_score'] = content_to_score.get(entry['content'], 0.0)
    # Sort by rerank_score
    reranked = sorted(results, key=lambda x: x['rerank_score'], reverse=True)[:top_k]
    return reranked 


def compress_context(query: str, results: list[dict], top_n: int = 5) -> list[dict]:
    """
    Use the cross-encoder reranker to filter and compress a list of results (dicts with 'content') given a query.
    Returns only the most relevant chunks (top_n).
    """
    docs = [Document(page_content=entry['content']) for entry in results]
    compressed_docs = reranker.compress_documents(docs, query)
    # Map compressed docs back to original entries
    content_set = set(doc.page_content for doc in compressed_docs)
    compressed = [entry for entry in results if entry['content'] in content_set]
    return compressed[:top_n] 