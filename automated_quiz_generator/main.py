import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Query
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import dotenv
import redis
from retrievers import update_bm25, get_embeddings, get_index, get_relevant_documents
import requests
from quiz_generator import generate_quiz as llm_generate_quiz

dotenv.load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

app = FastAPI()

@app.post("/upload/")
async def upload_doc(file: UploadFile = File(...)):
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Load and extract text (PDF only for now)
    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    text = "\n".join([page.page_content for page in pages])
    os.remove(tmp_path)

    # Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = splitter.split_text(text)

    # Embed chunks with Nomic
    embeddings = get_embeddings()
    embeddings_list = embeddings.embed_documents(chunks)
    # Upsert to Pinecone with unique IDs
    index = get_index()
    if index:
        pinecone_vectors = [(f"chunk-{i}", vector) for i, vector in enumerate(embeddings_list)]
        index.upsert(vectors=pinecone_vectors)

    # Update BM25 and hybrid retrievers
    update_bm25(chunks)

    return {"message": f"Uploaded, split into {len(chunks)} chunks, and stored in Pinecone and BM25."}

@app.get("/generate_quiz/")
def generate_quiz(query: str = Query(...), difficulty: str = "medium"):
    # Retrieve relevant context
    retrieved_docs = get_relevant_documents(query)
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    context_hash = hash(context)
    cached = redis_client.get(f"quiz:{context_hash}")
    if cached is not None:
        # Redis returns bytes, decode to str
        if isinstance(cached, bytes):
            return {"quiz": cached.decode()}
        return {"quiz": str(cached)}
    # Generate quiz using langchain-groq
    quiz = llm_generate_quiz(context, difficulty)
    # Ensure only a string is stored in Redis
    if not isinstance(quiz, str):
        quiz = str(quiz)
    redis_client.set(f"quiz:{context_hash}", quiz)
    return {"quiz": quiz} 