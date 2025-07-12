"""
Data ingestion pipeline for sports analytics RAG system.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..utils.logging import get_logger
from ..config import get_settings
from ..vector_store.embeddings import NomicEmbeddings
from ..data.loaders import PDFLoader

logger = get_logger(__name__)


class DataIngestionPipeline:
    """Complete data ingestion pipeline for sports analytics."""
    
    def __init__(self):
        self.settings = get_settings()
        self.embeddings = NomicEmbeddings()
        self.text_splitter = self._init_text_splitter()
        
        logger.info("Data ingestion pipeline initialized")
    
    def _init_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Initialize text splitter for document chunking."""
        chunk_size = self.settings.chunk_size if self.settings else 1000
        chunk_overlap = self.settings.chunk_overlap if self.settings else 100
        
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self, data_dir: str = "data") -> List[Document]:
        """Load all documents from the data directory."""
        documents = []
        data_path = Path(data_dir)
        
        if not data_path.exists():
            logger.warning(f"Data directory {data_dir} does not exist")
            return documents
        
        # Load PDF files
        pdf_files = list(data_path.glob("*.pdf"))
        for pdf_file in pdf_files:
            try:
                logger.info(f"Loading PDF: {pdf_file}")
                loader = PDFLoader(str(pdf_file))
                pdf_docs = loader.load()
                
                # Add metadata
                for doc in pdf_docs:
                    doc.metadata.update({
                        "source": str(pdf_file),
                        "file_type": "pdf",
                        "file_name": pdf_file.name
                    })
                
                documents.extend(pdf_docs)
                logger.info(f"Loaded {len(pdf_docs)} pages from {pdf_file}")
                
            except Exception as e:
                logger.error(f"Error loading {pdf_file}: {e}")
        
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Chunk documents into smaller pieces for better retrieval."""
        if not documents:
            return documents
        
        try:
            chunked_docs = []
            
            for doc in documents:
                # Split the document content
                chunks = self.text_splitter.split_text(doc.page_content)
                
                # Create new documents for each chunk
                for i, chunk in enumerate(chunks):
                    chunk_doc = Document(
                        page_content=chunk,
                        metadata={
                            **doc.metadata,
                            "chunk_id": i,
                            "total_chunks": len(chunks),
                            "chunk_size": len(chunk)
                        }
                    )
                    chunked_docs.append(chunk_doc)
            
            logger.info(f"Chunked {len(documents)} documents into {len(chunked_docs)} chunks")
            return chunked_docs
            
        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            return documents
    
    def create_embeddings(self, documents: List[Document]) -> List[Document]:
        """Create embeddings for documents."""
        if not documents:
            return documents
        
        try:
            # Get embeddings for all documents
            texts = [doc.page_content for doc in documents]
            embeddings = self.embeddings.get_embeddings(texts)
            
            # Add embeddings to document metadata
            for doc, embedding in zip(documents, embeddings):
                doc.metadata["embedding"] = embedding
            
            logger.info(f"Created embeddings for {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return documents
    
    def store_in_vectorstore(self, documents: List[Document]) -> bool:
        """Store documents in Pinecone vector store."""
        try:
            from ..vector_store.pinecone_client import PineconeClient
            
            client = PineconeClient()
            
            # Store documents
            success = client.add_documents(documents)
            
            if success:
                logger.info(f"Successfully stored {len(documents)} documents in vector store")
            else:
                logger.error("Failed to store documents in vector store")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing in vector store: {e}")
            return False
    
    def run_full_pipeline(self, data_dir: str = "data") -> Dict[str, Any]:
        """Run the complete data ingestion pipeline."""
        try:
            logger.info("Starting data ingestion pipeline")
            
            # Step 1: Load documents
            documents = self.load_documents(data_dir)
            if not documents:
                return {"success": False, "error": "No documents loaded"}
            
            # Step 2: Chunk documents
            chunked_docs = self.chunk_documents(documents)
            
            # Step 3: Create embeddings
            docs_with_embeddings = self.create_embeddings(chunked_docs)
            
            # Step 4: Store in vector store
            storage_success = self.store_in_vectorstore(docs_with_embeddings)
            
            # Prepare results
            results = {
                "success": storage_success,
                "original_documents": len(documents),
                "chunked_documents": len(chunked_docs),
                "documents_with_embeddings": len(docs_with_embeddings),
                "storage_success": storage_success
            }
            
            if storage_success:
                logger.info("Data ingestion pipeline completed successfully")
            else:
                logger.error("Data ingestion pipeline failed at storage step")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in data ingestion pipeline: {e}")
            return {"success": False, "error": str(e)}
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get statistics about the ingestion pipeline."""
        try:
            # Test document loading
            documents = self.load_documents()
            
            # Test chunking
            chunked_docs = self.chunk_documents(documents)
            
            # Test embedding creation
            docs_with_embeddings = self.create_embeddings(chunked_docs)
            
            stats = {
                "original_documents": len(documents),
                "chunked_documents": len(chunked_docs),
                "documents_with_embeddings": len(docs_with_embeddings),
                "avg_chunk_size": sum(len(doc.page_content) for doc in chunked_docs) / len(chunked_docs) if chunked_docs else 0,
                "total_content_length": sum(len(doc.page_content) for doc in documents),
                "pipeline_components_working": {
                    "loading": len(documents) > 0,
                    "chunking": len(chunked_docs) > 0,
                    "embedding": len(docs_with_embeddings) > 0
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting pipeline stats: {e}")
            return {"error": str(e)}


def main():
    """Run the data ingestion pipeline."""
    pipeline = DataIngestionPipeline()
    
    # Run the full pipeline
    results = pipeline.run_full_pipeline()
    
    print("Data Ingestion Results:")
    print(f"Success: {results.get('success', False)}")
    print(f"Original Documents: {results.get('original_documents', 0)}")
    print(f"Chunked Documents: {results.get('chunked_documents', 0)}")
    print(f"Documents with Embeddings: {results.get('documents_with_embeddings', 0)}")
    
    if not results.get('success', False):
        print(f"Error: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main() 