# Document Compliance & Privacy Analyzer

A production-grade, multi-agent legal agreement auditor and privacy redaction engine built using **Python**, the **Google Agent Development Kit (ADK 2.0)**, and **Streamlit**.

This application implements a graph-based multi-agent execution pipeline that triages compliance policy contradictions in documents (e.g. NDAs and consulting contracts), verifies precedents against a simulated long-term legal registry, runs regex-based privacy filters, and provides a sleek **Human-in-the-Loop (HITL)** approval dashboard to resume/amend workflows.

---

## ✨ Features
- **ADK 2.0 Graph Workflow**: Sequential node orchestration (`START` -> `TriageNode` -> `MemoryNode` -> `RedactNode` -> `END`).
- **Policy Compliance Triage**: Detects governing law inconsistencies, overlapping intellectual property assignments, and liability capping contradictions.
- **Precedent Verification**: Integrates a long-term state registry (`compliance_registry.json`) to surface historical legal approvals and overrides.
- **Automated Data Privacy Redaction**: Automatically scans and strips PII including emails, telephone numbers, and cloud credentials (AWS keys).
- **Human-in-the-Loop validation**: Suspends execution and unlocks an interactive approval drawer inside Streamlit where legal auditors can verify, edit, and approve/reject drafts.
- **Stdio Model Context Protocol (MCP)**: Exposes workspace reading, writing, and document listing capabilities directly to MCP-compatible host environments.

---

## 📂 Project Directory Structure

```
capstone_vibecoding/
│
├── compliance_analyzer/
│   ├── __init__.py           # Package imports
│   ├── agents.py             # ADK 2.0 workflow nodes & graph layout
│   ├── config.py             # Contract policy rules & PII patterns
│   ├── tools.py              # SecureStreamReader path protection tool
│   └── mcp_server.py         # FastMCP Server implementation
│
├── app.py                    # Streamlit Visual Stepper Dashboard
├── mcp_config.json           # Model Context Protocol registration config
├── NonDisclosureAgreement.txt # Sample NDA with policy issues and PII
├── ConsultingAgreement.txt   # Sample Consulting contract with issues and PII
├── COMPLIANCE_ANALYZER_ARCHITECTURE.md # Full design and testing spec sheet
├── requirements.txt          # Python package requirements
├── run.bat                   # Windows batch file startup script
└── run.ps1                   # PowerShell startup script
```

## 🚀 GitHub Repository Deployment Guide

To deploy the Document Compliance & Privacy Analyzer directly from the GitHub repository:

### 1. Clone the Repository
Clone the codebase to your local system:
```bash
git clone https://github.com/purusothaman-raghu/kaggle-capstone.git
cd kaggle-capstone
```

### 2. Configure Virtual Environment & Install Dependencies
It is highly recommended to use a Python virtual environment to isolate library dependencies:

**On Windows:**
```powershell
python3 -m venv .venv
# or: python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Launch the Application
Start the Streamlit dashboard server:

**Using Startup Scripts (Windows):**
Double-click `run.bat` or run `.\run.ps1` in PowerShell.

**Manual Command (Any Platform):**
```bash
python3 -m streamlit run app.py
# or: python -m streamlit run app.py
```

Open your browser to:
👉 [http://localhost:8501](http://localhost:8501)

### 3. Load Sample Documents
- The application root contains two pre-configured sample files for instant audit testing:
  - **[NonDisclosureAgreement.txt](NonDisclosureAgreement.txt)**
  - **[ConsultingAgreement.txt](ConsultingAgreement.txt)**
- Use the **Load Sample** buttons on the dashboard to populate the editor and click **Analyze Compliance & Privacy** to run the workflow.

---

## 📘 Design & Test Execution Docs
For deep details about the graph node schema, state variables, FastMCP stdio interface details, and the validation verification test logs, review our:
👉 **[COMPLIANCE_ANALYZER_ARCHITECTURE.md](COMPLIANCE_ANALYZER_ARCHITECTURE.md)**
