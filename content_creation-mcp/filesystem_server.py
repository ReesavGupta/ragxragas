from ast import List
from typing import Dict
from fastmcp import FastMCP
import os
from datetime import datetime

WORKSPACE = os.path.abspath("./content-workspace")

def safe_join(base, *paths):
    # Prevent directory traversal
    final_path = os.path.abspath(os.path.join(base, *paths))
    if not final_path.startswith(base):
        raise ValueError("Path outside workspace!")
    return final_path

mcp = FastMCP(name="Content Filesystem MCP")

@mcp.tool
def ping() -> dict:
    return {"message": "pong"}

@mcp.tool
def write_file(relative_path: str, content: str) -> str:
    abs_path = safe_join(WORKSPACE, relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    return "File written."

@mcp.tool
def read_file(relative_path: str) -> str:
    abs_path = safe_join(WORKSPACE, relative_path)
    with open(abs_path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool
def list_directory(relative_dir: str) -> list:
    abs_dir = safe_join(WORKSPACE, relative_dir)
    return os.listdir(abs_dir)

@mcp.tool
def edit_file(relative_path: str, new_content: str) -> str:
    abs_path = safe_join(WORKSPACE, relative_path)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return "File edited."

@mcp.tool
def move_file(src_relative: str, dst_relative: str) -> str:
    abs_src = safe_join(WORKSPACE, src_relative)
    abs_dst = safe_join(WORKSPACE, dst_relative)
    os.makedirs(os.path.dirname(abs_dst), exist_ok=True)
    os.rename(abs_src, abs_dst)
    return "File moved."

if __name__ == "__main__":
    mcp.run(transport="http", port=8080,   stateless_http=True) 