# Document Compliance and Privacy Analyzer

This document details the architecture, directory layout, multi-agent workflow, and execution guide for the production-grade **Document Compliance and Privacy Analyzer** built inside this sandbox environment using the **Agent Development Kit (ADK 2.0)**, Python, and Streamlit.

---

## 🏗️ Multi-Agent Graph Architecture

The compliance analyzer orchestrates three specialized agentic nodes connected sequentially in a directed graph using the ADK 2.0 Workflow engine. If a compliance warning or PII is flagged, the runtime pauses for a **Human-in-the-Loop (HITL)** approval step at the final node.

```mermaid
graph LR
    START[START] --> TriageNode[TriageNode]
    TriageNode --> |Compliance Warnings| MemoryNode[MemoryNode]
    MemoryNode --> |Historical Precedents| RedactNode[RedactNode]
    RedactNode --> |HITL Interrupt / Verification| END[END]
    
    style START fill:#198754,stroke:#fff,stroke-width:2px,color:#fff
    style TriageNode fill:#0d6efd,stroke:#fff,stroke-width:2px,color:#fff
    style MemoryNode fill:#0d6efd,stroke:#fff,stroke-width:2px,color:#fff
    style RedactNode fill:#fd7e14,stroke:#fff,stroke-width:2px,color:#fff
    style END fill:#198754,stroke:#fff,stroke-width:2px,color:#fff
```

### 1. `TriageNode`
- **Purpose**: Extracts document contents (supports files and text streams) securely.
- **Auditing**: Performs static analysis against the `compliance_analyzer/config.py` ruleset to detect conflicting clauses.
- **Conflicts Triaged**:
  - **Governing Law Inconsistencies**: Multiple jurisdictions (e.g. California vs New York) within the same contract.
  - **Liability Inconsistencies**: Contradictions between capped liability clauses and unlimited indemnification clauses.
  - **IP Assignment Disputes**: Conflicting ownership assignments (e.g. exclusive assignment vs shared/joint licensing).

### 2. `MemoryNode`
- **Purpose**: Simulates a long-term state registry (persistence layer) checking for previously flagged patterns.
- **Auditing**: Queries the `compliance_registry.json` database to see if matching violations have historical precedents or legal resolution overrides.

### 3. `RedactNode`
- **Purpose**: Handles PII privacy redaction and hosts the Human-in-the-Loop gate.
- **Privacy Redactions**: Automatically scans and replaces raw PII with placeholder tokens (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_API_KEY]`).
- **HITL Integration**: Yields an ADK `RequestInput` interrupt. The workflow pauses execution, returning control to the Streamlit frontend. Upon user validation ("Approve & Redact" or "Reject"), the workflow resumes, writes the audited version to disk, and updates the compliance state.

---

## 📂 Project Directory Layout

```
capstone_vibecoding/
│
├── compliance_analyzer/
│   ├── __init__.py           # Package exports
│   ├── agents.py             # ADK 2.0 Nodes and Workflow definition
│   ├── config.py             # Compliance clauses and PII regex config
│   ├── tools.py              # SecureStreamReader helper class
│   └── mcp_server.py         # FastMCP Server exposing secure tools
│
├── app.py                    # Sleek Streamlit Frontend Dashboard
├── mcp_config.json           # MCP profile server configuration
├── NonDisclosureAgreement.txt # Sample document containing conflicts and PII
├── run.bat                   # Windows batch file execution script
└── run.ps1                   # PowerShell execution script
```

---

## 🔌 Embedded Tooling & MCP Integration

- **`SecureStreamReader`**: A sandbox-secured helper tool that maps text/JSON streams. It validates all relative paths to prevent directory traversal outside of the workspace directory.
- **Model Context Protocol (MCP)**:
  - Built with Python's FastMCP framework, exposing document read/write and listing capabilities directly.
  - Configured in the local `mcp_config.json` profile, enabling direct integration of workspace files into the context loop.

---

## 🎨 Streamlit Frontend Design

The frontend has been styled for **Rich Aesthetics** using standard Streamlit components, custom HTML/CSS, and Google Fonts.
- **Interactive File Hub**: Allows drag-and-drop file uploads, manual text input, and single-click loading of the sample NDA document.
- **Real-Time Graph visualization**: Highlights the active node executing in the graph pipeline with color changes (Blue: Active, Green: Completed, Orange: Interrupted).
- **Human-in-the-Loop Panel**: Dynamically displays flagged warnings, historical precedent resolutions, and a live text editor showing the draft document. Reviewers can edit the redacted text and click **Approve & Redact** or **Reject** to resume the workflow.

---

## 🚀 Execution Guide

To start the Document Compliance & Privacy Analyzer, run either of the startup scripts from your terminal in the workspace directory:

### Windows Command Prompt
```cmd
run.bat
```

### PowerShell
```powershell
.\run.ps1
```

Once running, open your web browser to the URL printed in the terminal (typically `http://localhost:8501`).
