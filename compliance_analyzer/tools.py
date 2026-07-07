import os
import json
from typing import Any, Dict

class SecureStreamReader:
    """A helper tool class that reads text/JSON streams securely within the sandbox.
    
    It prevents path traversal and ensures files are read strictly from the workspace.
    """
    def __init__(self, workspace_dir: str):
        self.workspace_dir = os.path.abspath(workspace_dir)

    def _resolve_and_validate_path(self, relative_path: str) -> str:
        # Prevent directory traversal
        abs_path = os.path.abspath(os.path.join(self.workspace_dir, relative_path))
        if not abs_path.startswith(self.workspace_dir):
            raise PermissionError(f"Access Denied: Path '{relative_path}' is outside workspace '{self.workspace_dir}'.")
        return abs_path

    def read_text_file(self, filename: str) -> str:
        """Securely reads a text file from the workspace."""
        path = self._resolve_and_validate_path(filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {filename}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def read_json_file(self, filename: str) -> Any:
        """Securely reads a JSON file from the workspace."""
        content = self.read_text_file(filename)
        return json.loads(content)

    def write_text_file(self, filename: str, content: str) -> None:
        """Securely writes a text file to the workspace."""
        path = self._resolve_and_validate_path(filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def write_json_file(self, filename: str, data: Any) -> None:
        """Securely writes JSON data to a file in the workspace."""
        path = self._resolve_and_validate_path(filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
