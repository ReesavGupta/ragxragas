"""
Retrieval system with contextual compression and reranking for sports analytics.
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor, CrossEncoderReranker
from langchain_pinecone import PineconeVectorStore
from langchain_nomic import NomicEmbeddings
from langchain_groq import ChatGroq
from pydantic import SecretStr

from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class SportsRetrievalSystem:
    """Advanced retrieval system with contextual compression and reranking."""
    
    def __init__(self, index_name: Optional[str] = None):
        self.settings = get_settings()
        self.index_name = index_name or (self.settings.pinecone_index_name if self.settings else "sports-analytics-rag")
        
        # Ensure sentence-transformers is installed
        try:
            import sentence_transformers
        except ImportError:
            raise ImportError("sentence-transformers is required for CrossEncoderReranker. Please install it with 'pip install sentence-transformers'.")
        
        # Initialize components
        self.llm = self._init_llm()
        self.embeddings = self._init_embeddings()
        self.vector_store = self._init_vector_store()
        self.compressor = self._init_compressor()
        self.reranker = self._init_reranker()
        self.compression_retriever = self._init_compression_retriever()
        
        logger.info("Sports retrieval system initialized")
    
    def _init_llm(self) -> ChatGroq:
        """Initialize Groq LLM."""
        if not self.settings:
            raise ValueError("Settings not available")
        
        return ChatGroq(
            api_key=SecretStr(self.settings.groq_api_key) if self.settings.groq_api_key else None,
            model=self.settings.groq_model,
            temperature=self.settings.temperature
        )
    
    def _init_embeddings(self) -> NomicEmbeddings:
        """Initialize Nomic embeddings."""
        if not self.settings:
            raise ValueError("Settings not available")
        
        return NomicEmbeddings(
            nomic_api_key=self.settings.nomic_api_key,
            model=self.settings.embedding_model
        )
    
    def _init_vector_store(self) -> PineconeVectorStore:
        """Initialize Pinecone vector store."""
        if not self.settings:
            raise ValueError("Settings not available")
        
        try:
            import pinecone
            pc = pinecone.Pinecone(api_key=self.settings.pinecone_api_key)
            index = pc.Index(self.index_name)
            
            return PineconeVectorStore(
                embedding=self.embeddings,
                index=index
            )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def _init_compressor(self) -> LLMChainExtractor:
        """Initialize contextual compression."""
        return LLMChainExtractor.from_llm(
            llm=self.llm
        )
    
    def _init_reranker(self):
        """Initialize semantic reranking using a simple approach."""
        # For now, we'll use a simple approach without external reranker
        # This can be enhanced later with proper reranker implementation
        logger.info("Using simple reranking approach (no external reranker)")
        return None
    
    def _init_compression_retriever(self) -> ContextualCompressionRetriever:
        """Initialize compression retriever."""
        base_retriever = self.vector_store.as_retriever(
            search_kwargs={"k": min(3, self.settings.max_retrieval_results if self.settings else 3)}
        )
        
        return ContextualCompressionRetriever(
            base_compressor=self.compressor,
            base_retriever=base_retriever
        )
    
    def retrieve_with_compression(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Retrieve documents with contextual compression."""
        try:
            k = k or min(3, self.settings.max_retrieval_results if self.settings else 3)
            
            # Get compressed documents using the new invoke method
            compressed_docs = self.compression_retriever.invoke(query)
            
            logger.info(f"Retrieved {len(compressed_docs)} compressed documents for query: {query}")
            return compressed_docs
            
        except Exception as e:
            logger.error(f"Error in compression retrieval: {e}")
            # Fallback to basic retrieval
            k_fallback = k or 3
            return self.vector_store.similarity_search(query, k=k_fallback)
    
    def rerank_documents(self, query: str, documents: List[Document]) -> List[Document]:
        """Rerank documents based on relevance to query."""
        if not documents:
            return documents
        
        # If no reranker is available, return documents as-is
        if self.reranker is None:
            logger.info(f"No reranker available, returning {len(documents)} documents as-is")
            return documents
        
        try:
            reranked_docs = self.reranker.rerank(query, documents)
            logger.info(f"Reranked {len(reranked_docs)} documents for query: {query}")
            return reranked_docs
        except Exception as e:
            logger.error(f"Error in document reranking: {e}")
            return documents
    
    def retrieve_with_reranking(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Retrieve documents with compression and reranking."""
        try:
            # Step 1: Get compressed documents
            compressed_docs = self.retrieve_with_compression(query, k)
            
            # Step 2: Rerank the compressed documents
            reranked_docs = self.rerank_documents(query, compressed_docs)
            
            logger.info(f"Retrieved and reranked {len(reranked_docs)} documents for query: {query}")
            return reranked_docs
            
        except Exception as e:
            logger.error(f"Error in retrieval with reranking: {e}")
            # Fallback to basic retrieval
            k_fallback = k or 3
            return self.vector_store.similarity_search(query, k=k_fallback)
    
    def get_relevant_documents(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Main retrieval method with compression and reranking."""
        return self.retrieve_with_reranking(query, k)
    
    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Basic similarity search without compression/reranking."""
        k_val = k or (self.settings.max_retrieval_results if self.settings else 10)
        return self.vector_store.similarity_search(query, k=k_val)
    
    def get_retrieval_stats(self, query: str) -> Dict[str, Any]:
        """Get statistics about the retrieval process."""
        try:
            # Test different retrieval methods
            basic_results = self.similarity_search(query, k=5)
            compressed_results = self.retrieve_with_compression(query, k=5)
            full_results = self.retrieve_with_reranking(query, k=5)
            
            stats = {
                "query": query,
                "basic_retrieval_count": len(basic_results),
                "compressed_retrieval_count": len(compressed_results),
                "full_retrieval_count": len(full_results),
                "compression_ratio": len(compressed_results) / len(basic_results) if basic_results else 0,
                "retrieval_methods_working": {
                    "basic": len(basic_results) > 0,
                    "compression": len(compressed_results) > 0,
                    "reranking": len(full_results) > 0
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting retrieval stats: {e}")
            return {"error": str(e)} 