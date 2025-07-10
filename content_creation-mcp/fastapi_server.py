from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil
from typing import List
from openai_client import generate_article

app = FastAPI(title="Content Creation Assistant Backend")

# Base directory for content workspace
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../content-workspace'))

# Utility functions

def safe_join(base, *paths):
    # Prevent directory traversal
    final_path = os.path.abspath(os.path.join(base, *paths))
    if not final_path.startswith(base):
        raise HTTPException(status_code=400, detail="Invalid path.")
    return final_path

# Schemas
class FileListResponse(BaseModel):
    files: List[str]

class FileReadResponse(BaseModel):
    content: str

class FileWriteRequest(BaseModel):
    path: str
    content: str

class FileMoveRequest(BaseModel):
    src: str
    dst: str

class ArticleGenRequest(BaseModel):
    title: str
    summary: str
    tags: list

class ArticleGenResponse(BaseModel):
    draft: str

# Endpoints
@app.get("/list_files", response_model=FileListResponse)
def list_files(folder: str = ""):
    folder_path = safe_join(BASE_DIR, folder)
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found.")
    files = os.listdir(folder_path)
    return {"files": files}

@app.get("/read_file", response_model=FileReadResponse)
def read_file(path: str):
    file_path = safe_join(BASE_DIR, path)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content}

@app.post("/write_file")
def write_file(req: FileWriteRequest):
    file_path = safe_join(BASE_DIR, req.path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(req.content)
    return {"status": "success"}

@app.post("/move_file")
def move_file(req: FileMoveRequest):
    src_path = safe_join(BASE_DIR, req.src)
    dst_path = safe_join(BASE_DIR, req.dst)
    if not os.path.exists(src_path):
        raise HTTPException(status_code=404, detail="Source file not found.")
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.move(src_path, dst_path)
    return {"status": "success"}

@app.post("/generate_article", response_model=ArticleGenResponse)
def generate_article_endpoint(req: ArticleGenRequest = Body(...)):
    draft = generate_article(req.title, req.summary, req.tags)
    return {"draft": draft} 