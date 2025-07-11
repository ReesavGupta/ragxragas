import os
import sys
from redis import Redis
from rq import Queue, Worker
from dotenv import load_dotenv

# Use absolute import for WSL/Linux compatibility
from src.ingest import ingest_pdfs

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_conn = Redis.from_url(REDIS_URL)
queue = Queue("ingest", connection=redis_conn)

def enqueue_ingestion():
    # Disable job timeout for Windows compatibility
    job = queue.enqueue(ingest_pdfs, job_timeout=-1)
    print(f"Enqueued ingestion job: {job.id}")
    print("To start a worker, run: rq worker ingest")

if __name__ == "__main__":
    enqueue_ingestion() 