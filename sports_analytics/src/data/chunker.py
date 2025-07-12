"""
Document chunking utilities for sports analytics.
"""

from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

from ..utils.logging import get_logger
from ..utils.helpers import generate_chunk_id, sanitize_text
from ..config import get_settings

logger = get_logger(__name__)


class SportsDocumentChunker:
    """Chunker for sports analytics documents."""
    
    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        self.settings = get_settings()
        
        # Use settings or provided parameters
        self.chunk_size = chunk_size or (self.settings.chunk_size if self.settings else 1000)
        self.chunk_overlap = chunk_overlap or (self.settings.chunk_overlap if self.settings else 100)
        
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " | ", " ", ""]
        )
        
        logger.info(f"Initialized chunker with size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        if not documents:
            logger.warning("No documents provided for chunking")
            return []
        
        logger.info(f"Starting to chunk {len(documents)} documents")
        
        all_chunks = []
        total_chunks = 0
        
        for i, doc in enumerate(documents):
            try:
                # Clean the content
                clean_content = sanitize_text(doc.page_content)
                
                if not clean_content.strip():
                    logger.warning(f"Document {i} has no content after cleaning")
                    continue
                
                # Split the document
                chunks = self.text_splitter.split_text(clean_content)
                
                # Create Document objects for each chunk
                for j, chunk_content in enumerate(chunks):
                    if chunk_content.strip():
                        # Generate unique chunk ID
                        chunk_id = generate_chunk_id(chunk_content, doc.metadata.get("source", "unknown"))
                        
                        # Create metadata for the chunk
                        chunk_metadata = doc.metadata.copy()
                        chunk_metadata.update({
                            "chunk_id": chunk_id,
                            "chunk_index": j,
                            "total_chunks": len(chunks),
                            "original_document_index": i,
                            "chunk_size": len(chunk_content)
                        })
                        
                        # Create new document for the chunk
                        chunk_doc = Document(
                            page_content=chunk_content,
                            metadata=chunk_metadata
                        )
                        
                        all_chunks.append(chunk_doc)
                        total_chunks += 1
                
                logger.debug(f"Document {i} split into {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error chunking document {i}: {e}")
                continue
        
        logger.info(f"Chunking completed: {len(documents)} documents -> {total_chunks} chunks")
        return all_chunks
    
    def chunk_single_document(self, document: Document) -> List[Document]:
        """Split a single document into chunks."""
        return self.chunk_documents([document])
    
    def validate_chunks(self, chunks: List[Document]) -> Dict[str, Any]:
        """Validate chunked documents and return statistics."""
        if not chunks:
            return {
                "total_chunks": 0,
                "average_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "empty_chunks": 0,
                "validation_passed": False
            }
        
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        empty_chunks = sum(1 for size in chunk_sizes if size == 0)
        
        stats = {
            "total_chunks": len(chunks),
            "average_chunk_size": sum(chunk_sizes) / len(chunks) if chunks else 0,
            "min_chunk_size": min(chunk_sizes) if chunk_sizes else 0,
            "max_chunk_size": max(chunk_sizes) if chunk_sizes else 0,
            "empty_chunks": empty_chunks,
            "validation_passed": empty_chunks == 0 and len(chunks) > 0
        }
        
        # Log validation results
        if stats["validation_passed"]:
            logger.info(f"Chunk validation passed: {stats}")
        else:
            logger.warning(f"Chunk validation failed: {stats}")
        
        return stats
    
    def get_chunk_statistics(self, chunks: List[Document]) -> Dict[str, Any]:
        """Get detailed statistics about chunks."""
        if not chunks:
            return {}
        
        # Group chunks by source
        source_stats = {}
        for chunk in chunks:
            source = chunk.metadata.get("source", "unknown")
            if source not in source_stats:
                source_stats[source] = {
                    "chunk_count": 0,
                    "total_size": 0,
                    "file_type": chunk.metadata.get("file_type", "unknown")
                }
            
            source_stats[source]["chunk_count"] += 1
            source_stats[source]["total_size"] += len(chunk.page_content)
        
        # Calculate overall statistics
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        
        stats = {
            "total_chunks": len(chunks),
            "total_content_size": sum(chunk_sizes),
            "average_chunk_size": sum(chunk_sizes) / len(chunks),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "source_statistics": source_stats,
            "unique_sources": len(source_stats)
        }
        
        return stats
    
    def filter_chunks_by_size(self, chunks: List[Document], min_size: int = 10, max_size: int = 10000) -> List[Document]:
        """Filter chunks by size constraints."""
        filtered_chunks = []
        
        for chunk in chunks:
            size = len(chunk.page_content)
            if min_size <= size <= max_size:
                filtered_chunks.append(chunk)
            else:
                logger.debug(f"Filtered out chunk of size {size} (outside range [{min_size}, {max_size}])")
        
        logger.info(f"Filtered {len(chunks)} chunks to {len(filtered_chunks)} chunks")
        return filtered_chunks
    
    def merge_small_chunks(self, chunks: List[Document], min_size: int = 100) -> List[Document]:
        """Merge small chunks with adjacent chunks."""
        if not chunks:
            return chunks
        
        merged_chunks = []
        current_chunk = None
        
        for chunk in chunks:
            if current_chunk is None:
                current_chunk = chunk
                continue
            
            # If current chunk is small, try to merge with next chunk
            if len(current_chunk.page_content) < min_size:
                # Merge content
                merged_content = current_chunk.page_content + "\n\n" + chunk.page_content
                
                # Update metadata
                merged_metadata = current_chunk.metadata.copy()
                merged_metadata.update({
                    "merged": True,
                    "original_chunks": 2,
                    "chunk_size": len(merged_content)
                })
                
                current_chunk = Document(
                    page_content=merged_content,
                    metadata=merged_metadata
                )
            else:
                # Current chunk is large enough, add it and start new chunk
                merged_chunks.append(current_chunk)
                current_chunk = chunk
        
        # Add the last chunk
        if current_chunk:
            merged_chunks.append(current_chunk)
        
        logger.info(f"Merged chunks: {len(chunks)} -> {len(merged_chunks)}")
        return merged_chunks 