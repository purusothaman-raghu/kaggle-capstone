# Manual Testing Guide for MCP Servers (Direct CLI)

Because MCP servers using stdio transport communicate using JSON-RPC 2.0 messages over standard input/output (`stdin`/`stdout`), you can test them directly from your shell by running the server and feeding it JSON commands.

> [!WARNING]
> The stdio protocol expects single-line JSON messages. Make sure your message does not contain literal newlines inside the JSON structure when sending it.

### Step-by-Step CLI Execution

1. Set the `PYTHONPATH` environment variable and start the server:
   ```powershell
   # In PowerShell:
   $env:PYTHONPATH="."
   python -m compliance_analyzer.mcp_server
   ```

   ```cmd
   # In Command Prompt (CMD):
   set PYTHONPATH=.
   python -m compliance_analyzer.mcp_server
   ```
   *(The terminal will sit waiting for input. It will not print anything until it receives a valid protocol message).*

2. Paste the **Initialize Request** into the terminal and press **Enter**:
   ```json
   {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "manual-test", "version": "1.0.0"}}}
   ```
   The server should reply with a JSON response containing its capabilities and info.

3. List the available tools by pasting this request and pressing **Enter**:
   ```json
   {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
   ```
   The server will return a list of tools including `list_workspace_documents`, `read_document_stream`, etc.

4. Call a tool (e.g. `list_workspace_documents`) by pasting this request and pressing **Enter**:
   ```json
   {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_workspace_documents", "arguments": {}}}
   ```

5. Exit the server:
   Press `Ctrl+C` or close the terminal.
