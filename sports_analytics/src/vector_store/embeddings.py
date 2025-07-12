"""
Embedding generation utilities for sports analytics using LangChain Nomic integration.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from langchain.schema import Document
from langchain_nomic import NomicEmbeddings as LangChainNomicEmbeddings

from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class NomicEmbeddings:
    """Wrapper for LangChain Nomic embeddings with error handling and caching."""
    
    def __init__(self, model_name: Optional[str] = None):
        self.settings = get_settings()
        self.model_name = model_name or (self.settings.embedding_model if self.settings else "nomic-embed-text-v1.5")
        
        try:
            self.embeddings = LangChainNomicEmbeddings(
                model=self.model_name,
                nomic_api_key=self.settings.nomic_api_key if self.settings else None
            )
            logger.info(f"Initialized LangChain Nomic embeddings with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Nomic embeddings: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            # Return zero vector as fallback
            return [0.0] * 768  # Default dimension for nomic embeddings
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings for {len(texts)} texts: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 768 for _ in texts]
    
    def get_document_embeddings(self, documents: List[Document]) -> List[List[float]]:
        """Generate embeddings for document contents."""
        texts = [doc.page_content for doc in documents]
        return self.get_embeddings(texts)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        try:
            # Test embedding to get dimension
            test_embedding = self.get_embedding("test")
            return len(test_embedding)
        except Exception as e:
            logger.error(f"Error getting embedding dimension: {e}")
            return 768  # Default dimension


class EmbeddingValidator:
    """Validator for embedding quality and consistency."""
    
    @staticmethod
    def validate_embedding(embedding: List[float]) -> bool:
        """Validate that an embedding is reasonable."""
        if not embedding:
            return False
        
        # Check for all zeros
        if all(x == 0.0 for x in embedding):
            return False
        
        # Check for NaN or infinite values
        if any(np.isnan(x) or np.isinf(x) for x in embedding):
            return False
        
        return True
    
    @staticmethod
    def validate_embeddings(embeddings: List[List[float]]) -> Dict[str, Any]:
        """Validate a list of embeddings and return statistics."""
        if not embeddings:
            return {
                "total_embeddings": 0,
                "valid_embeddings": 0,
                "invalid_embeddings": 0,
                "average_norm": 0.0,
                "validation_passed": False
            }
        
        valid_count = 0
        invalid_count = 0
        norms = []
        
        for embedding in embeddings:
            if EmbeddingValidator.validate_embedding(embedding):
                valid_count += 1
                # Calculate L2 norm
                norm = np.linalg.norm(embedding)
                norms.append(norm)
            else:
                invalid_count += 1
        
        stats = {
            "total_embeddings": len(embeddings),
            "valid_embeddings": valid_count,
            "invalid_embeddings": invalid_count,
            "average_norm": np.mean(norms) if norms else 0.0,
            "validation_passed": invalid_count == 0
        }
        
        if not stats["validation_passed"]:
            logger.warning(f"Embedding validation failed: {invalid_count} invalid embeddings")
        
        return stats
    
    @staticmethod
    def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Normalize vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0 