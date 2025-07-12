"""
Main FastAPI application for the Sports Analytics RAG System.
"""

import time
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings, validate_environment
from .models import (
    QueryRequest, QueryResponse, DecomposeRequest, DecomposeResponse,
    HealthResponse, MetricsResponse, ErrorResponse
)
from .utils.logging import setup_logging, get_logger
from dotenv import load_dotenv

load_dotenv()
# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sports Analytics RAG System",
    description="Advanced sports analytics RAG system with query decomposition and citation-based responses",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global metrics
metrics = {
    "total_queries": 0,
    "total_processing_time": 0.0,
    "successful_queries": 0,
    "failed_queries": 0
}


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting Sports Analytics RAG System")
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed")
        raise RuntimeError("Environment validation failed")
    
    logger.info("Environment validation passed")
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Sports Analytics RAG System")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    
    services = {
        "groq_api": "unknown",
        "pinecone": "unknown",
        "nomic": "unknown"
    }
    
    # TODO: Add actual service health checks
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat(),
        services=services
    )


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get system metrics."""
    avg_response_time = (
        metrics["total_processing_time"] / metrics["total_queries"]
        if metrics["total_queries"] > 0
        else 0.0
    )
    
    success_rate = (
        (metrics["successful_queries"] / metrics["total_queries"]) * 100
        if metrics["total_queries"] > 0
        else 0.0
    )
    
    return MetricsResponse(
        total_queries=metrics["total_queries"],
        average_response_time=avg_response_time,
        success_rate=success_rate,
        active_connections=0,  # TODO: Implement connection tracking
        memory_usage={}  # TODO: Implement memory tracking
    )


@app.post("/decompose", response_model=DecomposeResponse)
async def decompose_query(request: DecomposeRequest):
    """Decompose a complex query into sub-questions."""
    start_time = time.time()
    
    try:
        # Initialize query decomposer
        from .rag.decomposition import QueryDecomposer
        decomposer = QueryDecomposer()
        
        # Decompose the query
        sub_questions = decomposer.decompose_query(request.query)
        
        processing_time = time.time() - start_time
        
        logger.info(
            "Query decomposed",
            query=request.query,
            sub_questions=sub_questions,
            processing_time=processing_time
        )
        
        return DecomposeResponse(
            sub_questions=sub_questions,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error decomposing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=QueryResponse)
async def ask_query(request: QueryRequest):
    """Process a sports analytics query."""
    start_time = time.time()
    
    try:
        # Update metrics
        metrics["total_queries"] += 1
        
        # Initialize RAG pipeline
        from .rag.generation import SportsRAGPipeline
        rag_pipeline = SportsRAGPipeline()
        
        # Process the query
        result = rag_pipeline.answer_complex_query(request.query)
        
        processing_time = time.time() - start_time
        
        # Update metrics
        metrics["total_processing_time"] += processing_time
        metrics["successful_queries"] += 1
        
        # Prepare response
        answer = result.get("final_answer", "No answer generated")
        sub_questions = result.get("sub_questions", [])
        confidence_score = result.get("overall_confidence", 0.0)
        
        # Prepare citations from sub-answers
        citations = []
        for sub_answer in result.get("sub_answers", []):
            for source in sub_answer.get("sources", []):
                citation = {
                    "source": source.get("source", "unknown"),
                    "content": source.get("content", ""),
                    "relevance_score": sub_answer.get("confidence", 0.0)
                }
                citations.append(citation)
        
        logger.info(
            "Query processed",
            query=request.query,
            processing_time=processing_time,
            answer_length=len(answer),
            sub_questions_count=len(sub_questions)
        )
        
        return QueryResponse(
            answer=answer,
            citations=citations,
            processing_time=processing_time,
            sub_questions=sub_questions,
            confidence_score=confidence_score
        )
        
    except Exception as e:
        metrics["failed_queries"] += 1
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Sports Analytics RAG System",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    } 