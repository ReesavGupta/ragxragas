"""
Pydantic models for the Sports Analytics RAG API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for sports analytics queries."""
    
    query: str = Field(..., description="The sports analytics query to process")
    include_citations: bool = Field(default=True, description="Whether to include citations in the response")
    max_results: Optional[int] = Field(default=10, description="Maximum number of retrieval results")


class Citation(BaseModel):
    """Model for source citations."""
    
    source: str = Field(..., description="Source document or file name")
    content: str = Field(..., description="Relevant content from the source")
    relevance_score: float = Field(..., description="Relevance score of the citation")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    chunk_id: Optional[str] = Field(None, description="Chunk identifier")


class QueryResponse(BaseModel):
    """Response model for sports analytics queries."""
    
    answer: str = Field(..., description="The generated answer to the query")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    processing_time: float = Field(..., description="Time taken to process the query in seconds")
    sub_questions: List[str] = Field(default_factory=list, description="Decomposed sub-questions")
    confidence_score: Optional[float] = Field(None, description="Confidence score of the answer")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DecomposeRequest(BaseModel):
    """Request model for query decomposition."""
    
    query: str = Field(..., description="The complex query to decompose")


class DecomposeResponse(BaseModel):
    """Response model for query decomposition."""
    
    sub_questions: List[str] = Field(..., description="List of decomposed sub-questions")
    processing_time: float = Field(..., description="Time taken to decompose the query")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Current timestamp")
    services: Dict[str, str] = Field(default_factory=dict, description="Status of external services")


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""
    
    total_queries: int = Field(..., description="Total number of queries processed")
    average_response_time: float = Field(..., description="Average response time in seconds")
    success_rate: float = Field(..., description="Success rate percentage")
    active_connections: int = Field(..., description="Number of active connections")
    memory_usage: Dict[str, Any] = Field(default_factory=dict, description="Memory usage statistics")


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp") 