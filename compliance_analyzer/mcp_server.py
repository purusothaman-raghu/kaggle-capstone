import os
import sys
from mcp.server.fastmcp import FastMCP
from compliance_analyzer.tools import SecureStreamReader

# Use current directory as workspace
WORKSPACE_PATH = os.path.abspath(os.getcwd())
reader = SecureStreamReader(WORKSPACE_PATH)

mcp = FastMCP("DocumentComplianceServer")

@mcp.tool()
def read_document_stream(filename: str) -> str:
    """Reads a text or JSON stream securely from the workspace directory."""
    try:
        return reader.read_text_file(filename)
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_document_stream(filename: str, content: str) -> str:
    """Writes a text or JSON stream securely to the workspace directory."""
    try:
        reader.write_text_file(filename, content)
        return f"File successfully written to: {filename}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def list_workspace_documents() -> list[str]:
    """Lists text and JSON documents in the workspace directory."""
    files = []
    for root, _, filenames in os.walk(WORKSPACE_PATH):
        for f in filenames:
            # Skip hidden files and python caches/environments
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue
            if 'venv' in root or '__pycache__' in root:
                continue
            if f.endswith(('.txt', '.json', '.md', '.doc', '.docx')):
                rel_path = os.path.relpath(os.path.join(root, f), WORKSPACE_PATH)
                files.append(rel_path)
    return sorted(files)

if __name__ == "__main__":
    mcp.run(transport="stdio")
