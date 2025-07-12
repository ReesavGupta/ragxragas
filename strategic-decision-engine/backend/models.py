from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = 'documents'
    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    file_hash = Column(String, nullable=False, unique=True)
    status = Column(String, default='success')  # 'success' or 'failed'
    chunks = relationship('Chunk', back_populates='document')

class Chunk(Base):
    __tablename__ = 'chunks'
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey('documents.id'), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    # Add more metadata fields as needed (e.g., embedding_id, etc.)
    document = relationship('Document', back_populates='chunks') 