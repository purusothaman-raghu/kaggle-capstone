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

## 🖥️ How to Use the Streamlit Web Application

Once the Streamlit dashboard is running and accessible at `http://localhost:8501`, follow these steps to audit your documents:

### Step 1: Open the Dashboard
Open your web browser and navigate to [http://localhost:8501](http://localhost:8501). You will see a dark-themed legal auditor interface titled **Document Compliance & Privacy Analyzer**.

### Step 2: Load or Input a Document
You have three methods to load document content for auditing:
1. **Drag-and-drop file upload**: Drag and drop any text (`.txt`), markdown (`.md`), or JSON (`.json`) file into the **Document Input & Upload** area.
2. **Manual Text Entry**: Directly paste your legal contract text into the provided multi-line text editor.
3. **Use Pre-configured Samples**: Click the **📂 Load Conflicting NDA Sample** button below the text area to immediately populate the workspace with the preloaded NDA sample document.

### Step 3: Run the Compliance Audit
Click the large primary **🚀 Analyze Compliance & Privacy** button. This initializes the ADK 2.0 multi-agent workflow graph:
- You will see the **Workflow Execution Graph Status** stepper highlight nodes in real-time as they run.
- Real-time execution logs from the agents will populate inside the **Execution Agent Logs** console.

### Step 4: Complete the Human-in-the-Loop (HITL) Audit Review
When the graph reaches `RedactNode`, it will identify any PII or compliance contradictions and suspend execution. The **Human-in-the-Loop compliance validation required!** panel will appear on the right side:
1. **Review Flagged Conflicts**: View High and Medium severity policy warnings identified by `TriageNode` (e.g. governing law, liability caps, or IP joint ownership).
2. **Inspect Registry Matches**: Review historical approval overrides matching the contract clauses pulled from the persistent `MemoryNode` database.
3. **Analyze Privacy Redactions**: Inspect counts of redacted Emails, Phone Numbers, and API keys.
4. **Draft Verification & Manual Editing**: You can view the draft redacted document in the text editor and manually edit or override any redacted text.
5. **Add Auditor Comments**: Input any review comments or amendment notes in the text input box.

### Step 5: Grant Verdict (Approve / Reject)
- **Approve**: Click the green **✅ Approve & Redact** button. The workflow resumes, applies the draft text updates, writes the finalized document to your workspace (e.g. `NonDisclosureAgreement_redacted.txt`), and renders a download link.
- **Reject**: Click the red **❌ Reject Document** button. The workflow records the transaction as Rejected with your auditor comments, prompting the user to revise the original inputs.

---

## 📘 Design & Test Execution Docs
For deep details about the graph node schema, state variables, FastMCP stdio interface details, and the validation verification test logs, review our:
👉 **[COMPLIANCE_ANALYZER_ARCHITECTURE.md](COMPLIANCE_ANALYZER_ARCHITECTURE.md)**
