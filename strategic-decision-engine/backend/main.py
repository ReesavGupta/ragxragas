import os
import shutil
import hashlib
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
from core.processing import load_and_chunk_document
from core.embeddings import embed_chunks
from core.vector_store import upsert_embeddings, query_pinecone, get_bm25_retriever, hybrid_retrieve, rerank_results, compress_context
from backend.models import Document, Chunk
from backend.db import AsyncSessionLocal, get_db
from sqlalchemy.future import select
import uuid
import datetime
import redis

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def compute_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is missing in upload.")
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.pdf', '.docx', '.xlsx', '.csv', '.txt']:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Compute file hash for deduplication
    file_hash = compute_file_hash(temp_path)
    async with AsyncSessionLocal() as session:
        # Check for duplicate by file_hash
        result = await session.execute(select(Document).where(Document.file_hash == file_hash))
        existing_doc = result.scalars().first()
        if existing_doc:
            os.remove(temp_path)
            raise HTTPException(status_code=409, detail="Duplicate document detected.")

    # Chunk the document
    try:
        chunks = load_and_chunk_document(temp_path)
    except Exception as e:
        os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")

    # Generate embeddings
    try:
        embeddings = embed_chunks(chunks)
    except Exception as e:
        os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {e}")

    # Prepare chunk objects and metadata
    doc_id = str(uuid.uuid4())
    chunk_objs = []
    chunk_metadatas = []
    chunk_ids = []
    for idx, chunk in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        chunk_objs.append(Chunk(id=chunk_id, document_id=doc_id, chunk_index=idx, content=chunk))
        chunk_metadatas.append({
            "id": chunk_id,
            "document_id": doc_id,
            "filename": filename,
            "chunk_index": idx
        })
        chunk_ids.append(chunk_id)

    # Insert document and chunks, handle Pinecone upsert atomicity
    async with AsyncSessionLocal() as session:
        document = Document(id=doc_id, filename=filename, upload_time=datetime.datetime.utcnow(), file_hash=file_hash, status='success')
        session.add(document)
        session.add_all(chunk_objs)
        await session.commit()
        try:
            upsert_embeddings(embeddings, chunk_metadatas)
        except Exception as e:
            # Mark document as failed if Pinecone upsert fails
            document.status = 'failed' #type:ignore
            await session.commit()
            os.remove(temp_path)
            raise HTTPException(status_code=500, detail=f"Failed to upsert embeddings: {e}")
    os.remove(temp_path)

    # Store chunks in Redis for BM25
    for chunk_id, chunk in zip(chunk_ids, chunks):
        redis_client.set(f"chunk:{chunk_id}:text", chunk)
        redis_client.sadd("all_chunk_ids", chunk_id)

    return JSONResponse({
        "message": "Document uploaded and processed successfully.",
        "document_id": doc_id,
        "num_chunks": len(chunks),
        "chunk_ids": chunk_ids,
        "chunk_metadatas": chunk_metadatas
    })

@app.post("/search")
async def search_documents(query: str = Query(...), top_k: int = Query(5)):
    # Step 1: Query Pinecone for top-k relevant chunks
    pinecone_results = query_pinecone(query, top_k=top_k)
    chunk_ids = [result['id'] for result in pinecone_results]

    # Step 2: Fetch chunk content and metadata from PostgreSQL
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Chunk).where(Chunk.id.in_(chunk_ids)))
        chunk_objs = result.scalars().all()
        chunk_map = {chunk.id: chunk for chunk in chunk_objs}

    # Step 3: Merge Pinecone scores/metadata with DB content
    results = []
    for match in pinecone_results:
        chunk_id = match['id']
        chunk = chunk_map.get(chunk_id)
        if chunk:
            results.append({
                'id': chunk.id,
                'document_id': chunk.document_id,
                'chunk_index': chunk.chunk_index,
                'content': chunk.content,
                'score': match['score'],
                'metadata': match.get('metadata', {})
            })
    return {"results": results}

@app.post("/search_sparse")
async def search_sparse(query: str = Query(...), top_k: int = Query(5)):
    # Build BM25Retriever from Redis
    bm25_retriever = get_bm25_retriever(redis_client)
    # Retrieve top-k chunk texts
    results = bm25_retriever.get_relevant_documents(query)[:top_k]
    # Map chunk texts back to chunk IDs
    chunk_ids = redis_client.smembers("all_chunk_ids")  # type: ignore
    chunk_ids = [cid.decode() if isinstance(cid, bytes) else cid for cid in chunk_ids]  # type: ignore
    id_to_text = {redis_client.get(f"chunk:{cid}:text").decode(): cid for cid in chunk_ids}  # type: ignore
    response = []
    for doc in results:
        chunk_text = doc.page_content
        chunk_id = id_to_text.get(chunk_text)
        response.append({
            "chunk_id": chunk_id,
            "content": chunk_text,
            "score": doc.metadata.get('score', None)
        })
    return {"results": response}

@app.post("/search_hybrid")
async def search_hybrid(query: str = Query(...), top_k: int = Query(5)):
    results = hybrid_retrieve(query, top_k, redis_client)
    return {"results": results}

@app.post("/search_rerank")
async def search_rerank(query: str = Query(...), top_k: int = Query(5)):
    hybrid_results = hybrid_retrieve(query, top_k, redis_client)
    reranked = rerank_results(query, hybrid_results, top_k=top_k)
    return {"results": reranked}

@app.post("/search_compress")
async def search_compress(query: str = Query(...), top_k: int = Query(5)):
    hybrid_results = hybrid_retrieve(query, top_k, redis_client)
    compressed = compress_context(query, hybrid_results, top_n=top_k)
    return {"results": compressed} 