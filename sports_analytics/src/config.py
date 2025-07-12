"""
Configuration settings for the Sports Analytics RAG System.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    groq_api_key: str = ""
    pinecone_api_key: str = ""
    nomic_api_key: str = ""
    
    # Application Settings
    app_name: str = "Sports Analytics RAG"
    debug: bool = False
    log_level: str = "INFO"
    
    # Vector Database Settings
    pinecone_index_name: str = "sports-analytics-rag"
    
    # RAG Settings
    chunk_size: int = 800  # Smaller chunks for faster processing
    chunk_overlap: int = 50  # Reduced overlap
    max_retrieval_results: int = 3  # Reduced for faster retrieval
    
    # LLM Settings
    groq_model: str = "llama3-8b-8192"
    temperature: float = 0.05  # Lower temperature for faster, more deterministic responses
    
    # Embedding Settings
    embedding_model: str = "nomic-embed-text-v1.5"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings: Optional[Settings] = None

try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Please check your .env file and ensure all required variables are set")


def get_settings() -> Optional[Settings]:
    """Get the application settings."""
    return settings


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    required_vars = [
        "GROQ_API_KEY",
        "PINECONE_API_KEY",
        "NOMIC_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    
    return True 