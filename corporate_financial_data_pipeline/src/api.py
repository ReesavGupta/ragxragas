from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from src.rag_pipeline import RAGPipeline
from src.cache import AsyncRedisCache
from src.query_type_detection import detect_query_type_llm
from langchain_pinecone import PineconeVectorStore
from langchain_nomic import NomicEmbeddings
from pinecone import Pinecone
import asyncio
import os
import time
from typing import Dict
import hashlib
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Import groq RateLimitError for error handling
try:
    from groq import RateLimitError
except ImportError:
    RateLimitError = Exception  # fallback if groq not installed

app = FastAPI()

# Prometheus metrics
REQUEST_COUNT = Counter('rag_requests_total', 'Total RAG API requests', ['endpoint'])
CACHE_HIT_COUNT = Counter('rag_cache_hits_total', 'Total cache hits')
CACHE_MISS_COUNT = Counter('rag_cache_misses_total', 'Total cache misses')
ERROR_COUNT = Counter('rag_errors_total', 'Total errors')
REQUEST_LATENCY = Histogram('rag_request_latency_seconds', 'RAG API request latency', ['endpoint'])

class QueryRequest(BaseModel):
    query: str
    api_key: str

cache = AsyncRedisCache()

# API key management
API_KEYS = set(k.strip() for k in os.getenv("API_KEYS", "test-key").split(","))

# Simple in-memory rate limiting: {api_key: [timestamps]}
RATE_LIMIT = 60  # requests per minute
rate_limit_store: Dict[str, list] = {}

# TTLs in seconds
REALTIME_TTL = 3600
HISTORICAL_TTL = 86400

@app.on_event("startup")
async def startup_event():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index = os.getenv("PINECONE_INDEX_NAME")
    nomic_api_key = os.getenv("NOMIC_API_KEY")
    if not (pinecone_api_key and pinecone_index and nomic_api_key):
        raise RuntimeError("Missing Pinecone or Nomic environment variables.")
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(pinecone_index)
    vector_store = PineconeVectorStore(
        embedding=NomicEmbeddings(nomic_api_key=nomic_api_key, model="nomic-embed-text-v1.5"),
        index=index
    )
    app.state.vector_store = vector_store

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    REQUEST_COUNT.labels(endpoint="/query").inc()
    start_time = time.time()
    # API key authentication
    if not request.api_key or request.api_key not in API_KEYS:
        ERROR_COUNT.inc()
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    # Rate limiting
    now = time.time()
    window_start = now - 60
    timestamps = rate_limit_store.get(request.api_key, [])
    timestamps = [ts for ts in timestamps if ts > window_start]
    if len(timestamps) >= RATE_LIMIT:
        ERROR_COUNT.inc()
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    timestamps.append(now)
    rate_limit_store[request.api_key] = timestamps
    # LLM-based query type detection
    query_type = await detect_query_type_llm(request.query)
    ttl = REALTIME_TTL if query_type == "real_time" else HISTORICAL_TTL
    # Cache key: hash of query + query_type
    cache_key = hashlib.sha256(f"{request.query}:{query_type}".encode()).hexdigest()
    cached = await cache.get(cache_key)
    try:
        if cached:
            CACHE_HIT_COUNT.inc()
            return {"answer": cached["answer"], "context": cached["context"], "cached": True, "query_type": query_type}
        CACHE_MISS_COUNT.inc()
        rag_pipeline = RAGPipeline(vector_store=app.state.vector_store)
        result = await rag_pipeline.run(request.query)
        await cache.set(cache_key, result, ttl)
        return {"answer": result["answer"], "context": result["context"], "cached": False, "query_type": query_type}
    except RateLimitError as e:
        ERROR_COUNT.inc()
        raise HTTPException(status_code=429, detail="LLM rate limit reached. Please try again later.")
    except Exception as e:
        ERROR_COUNT.inc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        REQUEST_LATENCY.labels(endpoint="/query").observe(time.time() - start_time) 