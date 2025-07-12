"""
Pinecone vector store client for sports analytics.
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
import pinecone

from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class PineconeClient:
    """Pinecone vector store client for storing and retrieving documents."""
    
    def __init__(self, index_name: Optional[str] = None):
        self.settings = get_settings()
        self.index_name = index_name or (self.settings.pinecone_index_name if self.settings else "sports-analytics-rag")
        
        # Initialize Pinecone
        try:
            pc = pinecone.Pinecone(api_key=self.settings.pinecone_api_key if self.settings else "")
            self.index = pc.Index(self.index_name)
            logger.info(f"Initialized Pinecone client for index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the Pinecone index."""
        if not documents:
            logger.warning("No documents to add")
            return False
        
        try:
            vectors = []
            
            for i, doc in enumerate(documents):
                # Get embedding from document metadata
                embedding = doc.metadata.get("embedding")
                if not embedding:
                    logger.warning(f"Document {i} has no embedding, skipping")
                    continue
                
                # Prepare vector data
                vector_data = {
                    "id": f"doc_{i}_{doc.metadata.get('chunk_id', 0)}",
                    "values": embedding,
                    "metadata": {
                        "text": doc.page_content,  # LangChain expects 'text' field
                        "content": doc.page_content,  # Keep both for compatibility
                        "source": doc.metadata.get("source", "unknown"),
                        "file_type": doc.metadata.get("file_type", "unknown"),
                        "file_name": doc.metadata.get("file_name", "unknown"),
                        "chunk_id": doc.metadata.get("chunk_id", 0),
                        "total_chunks": doc.metadata.get("total_chunks", 1),
                        "chunk_size": doc.metadata.get("chunk_size", len(doc.page_content))
                    }
                }
                vectors.append(vector_data)
            
            if vectors:
                # Upsert vectors to Pinecone
                self.index.upsert(vectors=vectors)
                logger.info(f"Successfully added {len(vectors)} vectors to Pinecone")
                return True
            else:
                logger.warning("No valid vectors to add")
                return False
                
        except Exception as e:
            logger.error(f"Error adding documents to Pinecone: {e}")
            return False
    
    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar documents in the index."""
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return results.matches if hasattr(results, 'matches') else []
            
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"error": str(e)}
    
    def delete_all_vectors(self) -> bool:
        """Delete all vectors from the index."""
        try:
            self.index.delete(delete_all=True)
            logger.info("Successfully deleted all vectors from index")
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False 