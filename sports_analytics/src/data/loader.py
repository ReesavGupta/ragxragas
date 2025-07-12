"""
Data loading utilities for sports analytics.
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from langchain_community.document_loaders import (
    CSVLoader,
    JSONLoader,
    PyPDFLoader,
    DataFrameLoader
)
from langchain.schema import Document

from ..utils.logging import get_logger
from ..utils.helpers import extract_metadata_from_filename, sanitize_text
from ..config import get_settings

logger = get_logger(__name__)


class SportsDataLoader:
    """Loader for sports analytics data from various file formats."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.settings = get_settings()
        
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def load_csv_file(self, file_path: str) -> List[Document]:
        """Load data from CSV file."""
        try:
            full_path = self.data_dir / file_path
            
            if not full_path.exists():
                logger.warning(f"CSV file not found: {full_path}")
                return []
            
            # Load CSV with pandas first for better control
            df = pd.read_csv(full_path)
            
            # Convert to documents
            documents = []
            for index, row in df.iterrows():
                # Create text content from row
                content_parts = []
                for col, value in row.items():
                    if pd.notna(value):
                        content_parts.append(f"{col}: {value}")
                
                content = " | ".join(content_parts)
                content = sanitize_text(content)
                
                if content.strip():
                    metadata = {
                        "source": str(full_path),
                        "file_type": "csv",
                        "row_index": index,
                        "columns": list(df.columns),
                        "total_rows": len(df)
                    }
                    
                    doc = Document(
                        page_content=content,
                        metadata=metadata
                    )
                    documents.append(doc)
            
            logger.info(f"Loaded {len(documents)} documents from CSV: {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            return []
    
    def load_json_file(self, file_path: str) -> List[Document]:
        """Load data from JSON file."""
        try:
            full_path = self.data_dir / file_path
            
            if not full_path.exists():
                logger.warning(f"JSON file not found: {full_path}")
                return []
            
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                for index, item in enumerate(data):
                    content = self._json_to_text(item)
                    if content.strip():
                        metadata = {
                            "source": str(full_path),
                            "file_type": "json",
                            "item_index": index,
                            "total_items": len(data)
                        }
                        doc = Document(
                            page_content=content,
                            metadata=metadata
                        )
                        documents.append(doc)
            elif isinstance(data, dict):
                content = self._json_to_text(data)
                if content.strip():
                    metadata = {
                        "source": str(full_path),
                        "file_type": "json",
                        "structure": "object"
                    }
                    doc = Document(
                        page_content=content,
                        metadata=metadata
                    )
                    documents.append(doc)
            
            logger.info(f"Loaded {len(documents)} documents from JSON: {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return []
    
    def _json_to_text(self, obj: Any, prefix: str = "") -> str:
        """Convert JSON object to text representation."""
        if isinstance(obj, dict):
            parts = []
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    parts.append(f"{key}: {self._json_to_text(value, prefix + '  ')}")
                else:
                    parts.append(f"{key}: {value}")
            return " | ".join(parts)
        elif isinstance(obj, list):
            parts = []
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    parts.append(f"Item {i}: {self._json_to_text(item, prefix + '  ')}")
                else:
                    parts.append(f"Item {i}: {item}")
            return " | ".join(parts)
        else:
            return str(obj)
    
    def load_pdf_file(self, file_path: str) -> List[Document]:
        """Load data from PDF file."""
        try:
            full_path = self.data_dir / file_path
            
            if not full_path.exists():
                logger.warning(f"PDF file not found: {full_path}")
                return []
            
            # Use PyPDFLoader from langchain
            loader = PyPDFLoader(str(full_path))
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    "source": str(full_path),
                    "file_type": "pdf"
                })
            
            logger.info(f"Loaded {len(documents)} documents from PDF: {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading PDF file {file_path}: {e}")
            return []
    
    def load_all_files(self) -> List[Document]:
        """Load all supported files from the data directory."""
        all_documents = []
        
        if not self.data_dir.exists():
            logger.warning(f"Data directory does not exist: {self.data_dir}")
            return all_documents
        
        # Find all supported files
        csv_files = list(self.data_dir.glob("*.csv"))
        json_files = list(self.data_dir.glob("*.json"))
        pdf_files = list(self.data_dir.glob("*.pdf"))
        
        logger.info(f"Found {len(csv_files)} CSV files, {len(json_files)} JSON files, {len(pdf_files)} PDF files")
        
        # Load CSV files
        for csv_file in csv_files:
            documents = self.load_csv_file(csv_file.name)
            all_documents.extend(documents)
        
        # Load JSON files
        for json_file in json_files:
            documents = self.load_json_file(json_file.name)
            all_documents.extend(documents)
        
        # Load PDF files
        for pdf_file in pdf_files:
            documents = self.load_pdf_file(pdf_file.name)
            all_documents.extend(documents)
        
        logger.info(f"Total documents loaded: {len(all_documents)}")
        return all_documents
    
    def validate_data(self, documents: List[Document]) -> Dict[str, Any]:
        """Validate loaded data and return statistics."""
        if not documents:
            return {
                "total_documents": 0,
                "total_content_length": 0,
                "file_types": {},
                "sources": [],
                "validation_passed": False
            }
        
        stats = {
            "total_documents": len(documents),
            "total_content_length": sum(len(doc.page_content) for doc in documents),
            "file_types": {},
            "sources": [],
            "validation_passed": True
        }
        
        # Collect statistics
        for doc in documents:
            file_type = doc.metadata.get("file_type", "unknown")
            source = doc.metadata.get("source", "unknown")
            
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
            if source not in stats["sources"]:
                stats["sources"].append(source)
        
        # Validation checks
        if stats["total_documents"] == 0:
            stats["validation_passed"] = False
            logger.warning("No documents loaded")
        
        if stats["total_content_length"] == 0:
            stats["validation_passed"] = False
            logger.warning("No content found in documents")
        
        logger.info(f"Data validation completed: {stats}")
        return stats 