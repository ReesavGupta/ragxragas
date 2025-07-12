from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    CSVLoader,
    TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def load_and_chunk_document(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        loader = PyPDFLoader(file_path)
    elif ext == '.docx':
        loader = UnstructuredWordDocumentLoader(file_path)
    elif ext == '.xlsx':
        loader = UnstructuredExcelLoader(file_path)
    elif ext == '.csv':
        loader = CSVLoader(file_path)
    elif ext == '.txt':
        loader = TextLoader(file_path)
    else:
        raise ValueError(f'Unsupported file type: {ext}')

    documents = loader.load()
    # Each document is a Document object with .page_content
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    chunks = []
    for doc in documents:
        chunks.extend(text_splitter.split_text(doc.page_content))
    return chunks 