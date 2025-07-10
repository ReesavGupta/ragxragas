# Content Creation MCP

## Overview
This project provides a Managed Control Plane (MCP) for content creation workflows, exposing file and directory operations over HTTP using FastMCP. It is designed to be used as a backend for content management, automation, and AI-driven content generation tools.

## Features
- **FastMCP Server**: Exposes tools for file and directory operations via JSON-RPC 2.0 over HTTP.
- **Workspace Structure**: Manages a workspace with subdirectories for ideas, generated content, published content, and templates.
- **Python Client Boilerplate**: Includes a client for interacting with the MCP server.

## Directory Structure
```
content_creation-mcp/
  content-workspace/
    generated/
    ideas/
    published/
    templates/
  fastapi_server.py
  filesystem_server.py
  mcp_client.py
  openai_client.py
  streamlit_app.py
  requirements.txt
  PRD.md
```

## Status Report

### ✅ What is Working
- **FastMCP Server Setup**: Server starts successfully with `stateless_http=True` and exposes all intended tools (`ping`, `write_file`, `read_file`, `list_directory`, `edit_file`, `move_file`).
- **Directory Structure**: Workspace and all required subdirectories exist and are accessible.
- **Basic MCP Connectivity**: Server responds to JSON-RPC 2.0 requests at `/mcp/`. The `ping` tool is callable and returns a result (currently `{}` instead of `"pong"`).
- **Client Boilerplate**: Python client can send requests to the MCP server and is structured for all file operation tools.

### ⚠️ What is Not Working / Needs Attention
- **Tool Return Values**: The `ping` tool returns `{}` instead of `"pong"`. FastMCP may not be recognizing function return types properly (possible type annotation or environment issue).
- **Tool Parameter Validation**: All parameterized tools (e.g., `list_directory`, `write_file`) fail with "Invalid request parameters". FastMCP may not be parsing function signatures or type hints correctly.
- **Tool Table on Startup**: The tool signature table printed by FastMCP at startup should show parameter names and return types. If it does not, or shows `-> dict` for everything, this confirms a type introspection issue.
- **Environment Quirks**: Possible causes include:
  - Python version incompatibility
  - Mixed indentation or encoding issues in the source file
  - Stale `.pyc` files or `__pycache__` directories

## Troubleshooting
- **Check Python Version**: Ensure compatibility with FastMCP (Python 3.8+ recommended).
- **Clean Build Artifacts**: Delete `__pycache__/` and `.pyc` files to avoid stale bytecode issues.
- **Check Type Annotations**: Ensure all tool functions have correct type hints for parameters and return values.
- **Check Indentation/Encoding**: Use consistent indentation and UTF-8 encoding in all source files.
- **Review FastMCP Output**: On server startup, verify the tool signature table for correct parameter and return type introspection.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python filesystem_server.py
   ```
3. Interact with the server using the Python client or via HTTP/JSON-RPC requests (see `mcp_client.py` for examples).

## License
MIT License (see repository root for details) 