import itertools
import requests

MCP_SERVER_URL = "http://localhost:8080/mcp/"
HEADERS = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json"
}
_id_counter = itertools.count(1)

class MCPClientError(Exception):
    pass

def call_mcp_tool(tool, **kwargs):
    payload = {
        "jsonrpc": "2.0",
        "id": next(_id_counter),
        "method": tool,
        "params": kwargs
    }
    resp = requests.post(
        MCP_SERVER_URL,
        json=payload,
        headers=HEADERS,
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise MCPClientError(f"MCP Error {data['error']['code']}: {data['error']['message']}")
    return data["result"]

def write_file(relative_path, content):
    return call_mcp_tool("write_file", relative_path=relative_path, content=content)

def read_file(relative_path):
    return call_mcp_tool("read_file", relative_path=relative_path)

def list_directory(relative_dir):
    return call_mcp_tool("list_directory", relative_dir=relative_dir)

def edit_file(relative_path, new_content):
    return call_mcp_tool("edit_file", relative_path=relative_path, new_content=new_content)

def move_file(src_relative, dst_relative):
    return call_mcp_tool("move_file", src_relative=src_relative, dst_relative=dst_relative)

# Example usage:
if __name__ == "__main__":
    try:
        print("Directory contents:", list_directory(""))  # List root of workspace
        print("Writing file:", write_file("ideas/test.txt", "Hello, MCP!"))
        print("Reading file:", read_file("ideas/test.txt"))
        print("Editing file:", edit_file("ideas/test.txt", "Updated content"))
        print("Moving file:", move_file("ideas/test.txt", "generated/test.txt"))
        print("Directory contents (generated):", list_directory("generated"))
    except MCPClientError as e:
        print("MCP error:", e)
    except Exception as e:
        print("Request failed:", e)
