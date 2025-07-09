import os
import redis
from rq import Queue
from uuid import uuid4

# Connect to Redis (default: localhost:6379, override with REDIS_URL)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = redis.from_url(REDIS_URL)

# Create a queue (can use different names for different queues)
llm_queue = Queue("llm_requests", connection=redis_conn)

def enqueue_llm_request(func, *args, **kwargs):
    """
    Enqueue a function (e.g., LLMRouter.generate) with args/kwargs to the Redis queue.
    Returns a job ID for result retrieval.
    """
    job = llm_queue.enqueue(func, *args, **kwargs)
    return job.get_id()

def get_llm_result(job_id, timeout=30):
    """
    Fetch the result of a queued LLM request by job ID. Waits up to timeout seconds.
    """
    from rq.job import Job
    job = Job.fetch(job_id, connection=redis_conn)
    return job.result if job.is_finished else None

# Example usage (to be used in FastAPI or other API layer):
# job_id = enqueue_llm_request(llm_router.generate, question="What is RAG?", backend="ollama")
# result = get_llm_result(job_id) 