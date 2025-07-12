"""
Helper utility functions for the Sports Analytics RAG System.
"""

import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


def generate_chunk_id(content: str, source: str) -> str:
    """Generate a unique ID for a document chunk."""
    content_hash = hashlib.md5(content.encode()).hexdigest()
    source_hash = hashlib.md5(source.encode()).hexdigest()
    return f"{source_hash}_{content_hash}"


def calculate_relevance_score(query: str, content: str) -> float:
    """Calculate a simple relevance score between query and content."""
    query_words = set(query.lower().split())
    content_words = set(content.lower().split())
    
    if not query_words:
        return 0.0
    
    intersection = query_words.intersection(content_words)
    return len(intersection) / len(query_words)


def format_timestamp() -> str:
    """Format current timestamp in ISO format."""
    return datetime.now().isoformat()


def safe_json_serialize(obj: Any) -> str:
    """Safely serialize an object to JSON."""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return str(obj)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def extract_metadata_from_filename(filename: str) -> Dict[str, Any]:
    """Extract metadata from filename."""
    metadata = {
        "filename": filename,
        "file_type": filename.split(".")[-1] if "." in filename else "unknown",
        "source": filename
    }
    
    # Extract date if present in filename
    import re
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    date_match = re.search(date_pattern, filename)
    if date_match:
        metadata["date"] = date_match.group(1)
    
    return metadata


def merge_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge and deduplicate citations."""
    seen_sources = set()
    merged = []
    
    for citation in citations:
        source_key = f"{citation.get('source', '')}_{citation.get('chunk_id', '')}"
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            merged.append(citation)
    
    return merged


def validate_query(query: str) -> bool:
    """Validate that a query is reasonable."""
    if not query or not query.strip():
        return False
    
    if len(query.strip()) < 3:
        return False
    
    if len(query) > 1000:
        return False
    
    return True


def sanitize_text(text: str) -> str:
    """Sanitize text by removing potentially harmful characters."""
    import re
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Retry a function with exponential backoff."""
    import random
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable way."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s" 