import streamlit as st
import asyncio
import os
import json
import uuid
from typing import Any, Dict, List
from google.genai import types

# Setup premium layout and page configuration
st.set_page_config(
    page_title="Document Compliance & Privacy Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load helper tools and workflow
from google.adk import Runner, Event
from google.adk.sessions import InMemorySessionService
from compliance_analyzer import compliance_workflow, COMPLIANCE_RULES

# Inject Custom CSS for Rich Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply globally */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header and Title Styles */
    .app-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0d6efd, #0dcaf0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .app-subtitle {
        font-size: 1.1rem;
        color: #888899;
        margin-bottom: 2rem;
    }
    
    /* Premium card container styling */
    .premium-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Workflow step visualization boxes */
    .step-box {
        padding: 12px 18px;
        border-radius: 10px;
        font-weight: 600;
        text-align: center;
        min-width: 140px;
        border: 1px solid transparent;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    .step-pending {
        background: #18191f;
        color: #555566;
        border-color: #2b2d3a;
    }
    .step-active {
        background: rgba(13, 110, 253, 0.15);
        color: #0d6efd;
        border-color: #0d6efd;
        box-shadow: 0 0 15px rgba(13, 110, 253, 0.35);
        animation: pulse 1.5s infinite;
    }
    .step-completed {
        background: rgba(25, 135, 84, 0.15);
        color: #198754;
        border-color: #198754;
        box-shadow: 0 0 10px rgba(25, 135, 84, 0.15);
    }
    .step-interrupted {
        background: rgba(253, 126, 20, 0.15);
        color: #fd7e14;
        border-color: #fd7e14;
        box-shadow: 0 0 15px rgba(253, 126, 20, 0.35);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.02); opacity: 1; }
        100% { transform: scale(1); opacity: 0.8; }
    }
    
    /* Stats box layout */
    .stats-container {
        display: flex;
        gap: 15px;
        margin-bottom: 1rem;
    }
    .stat-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.user_id = "user_default"
    
if "runner" not in st.session_state:
    session_service = InMemorySessionService()
    st.session_state.runner = Runner(
        session_service=session_service,
        agent=compliance_workflow,
        app_name="compliance_analyzer",
        auto_create_session=True
    )

if "active_node" not in st.session_state:
    st.session_state.active_node = "START"
    st.session_state.node_statuses = {
        "TriageNode": "pending",
        "MemoryNode": "pending",
        "RedactNode": "pending"
    }

if "events" not in st.session_state:
    st.session_state.events = []
if "logs" not in st.session_state:
    st.session_state.logs = []

if "interrupted" not in st.session_state:
    st.session_state.interrupted = False
    st.session_state.interrupt_id = None
    st.session_state.interrupted_payload = None

if "wf_output" not in st.session_state:
    st.session_state.wf_output = None

if "document_name" not in st.session_state:
    st.session_state.document_name = ""

# Function to load samples
def load_sample():
    filepath = "NonDisclosureAgreement.txt"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            st.session_state.text_input = f.read()
            st.session_state.document_name = "NonDisclosureAgreement.txt"
    else:
        st.error("Sample document not found in workspace.")

# Sidebar Configuration and Info
with st.sidebar:
    st.markdown("### 🛠️ Configuration Profile")
    st.markdown("Edit the compliance patterns or view session details.")
    
    st.text_input("Active Session ID", value=st.session_state.session_id, disabled=True)
    st.text_input("User ID", value=st.session_state.user_id, disabled=True)
    
    st.markdown("---")
    st.markdown("### 📋 Conflicting Clause Rules")
    for rule in COMPLIANCE_RULES["conflicting_clauses"]:
        with st.expander(f"{rule['name']} ({rule['severity']})"):
            st.caption(rule["description"])
            st.code(", ".join(rule["patterns"]))
            
    st.markdown("---")
    st.markdown("### 🔒 PII Redaction Rules")
    for pii_type, pattern in COMPLIANCE_RULES["pii_patterns"].items():
        st.caption(f"Pattern for: **{pii_type.upper()}**")
        st.code(pattern)

# Top Bar / Title
st.markdown('<div class="app-header">Document Compliance & Privacy Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">A Production-Grade Multi-Agent Compliance Auditor using ADK 2.0 Graph Workflow</div>', unsafe_allow_html=True)

# Main Grid Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 📥 Document Input & Upload")
    
    # Drag-and-drop file uploader
    uploaded_file = st.file_uploader("Drag and drop document content here (.txt, .json, .md)", type=["txt", "json", "md"])
    
    # Manual text input area
    default_text = st.session_state.get("text_input", "")
    text_input = st.text_area("Or paste document content manually:", value=default_text, height=300, key="document_content_area")
    
    # Load sample NDA button
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("📂 Load Conflicting NDA Sample", use_container_width=True):
            load_sample()
            st.rerun()
    with col_btn2:
        if st.button("🧹 Clear Workspace", use_container_width=True):
            st.session_state.text_input = ""
            st.session_state.document_name = ""
            st.session_state.wf_output = None
            st.session_state.interrupted = False
            st.session_state.active_node = "START"
            st.session_state.node_statuses = {
                "TriageNode": "pending",
                "MemoryNode": "pending",
                "RedactNode": "pending"
            }
            st.session_state.logs = []
            st.session_state.events = []
            st.rerun()

    # Trigger analysis button
    st.markdown("---")
    start_btn = st.button("🚀 Analyze Compliance & Privacy", type="primary", use_container_width=True)

# ----------------- Helper functions for running the workflow -----------------
def process_event(event: Event):
    st.session_state.events.append(event)
    
    # Check node information to update graph statuses
    if event.node_info and event.node_info.path:
        path = event.node_info.path
        parts = path.split("/")
        node_part = parts[-1]  # like "TriageNode@1"
        node_name = node_part.split("@")[0]  # like "TriageNode"
        
        if node_name in st.session_state.node_statuses:
            st.session_state.active_node = node_name
            st.session_state.node_statuses[node_name] = "active"
            st.session_state.logs.append(f"🔄 Node [{node_name}] is executing...")
            
            # If the node has finalized its output, mark as completed
            if event.output is not None:
                st.session_state.node_statuses[node_name] = "completed"
                st.session_state.logs.append(f"✅ Node [{node_name}] successfully completed and returned output.")
                
    # Detect if the workflow was interrupted
    if event.long_running_tool_ids:
        st.session_state.interrupted = True
        st.session_state.interrupt_id = list(event.long_running_tool_ids)[0]
        
        # Extract payload from the event's function call
        fc = event.content.parts[0].function_call
        st.session_state.interrupted_payload = fc.args.get("payload", {})
        
        st.session_state.active_node = "RedactNode"
        st.session_state.node_statuses["RedactNode"] = "interrupted"
        st.session_state.logs.append("⚠️ Workflow paused at [RedactNode]. Awaiting human compliance approval.")

async def drive_workflow(input_content, doc_name="Text Input"):
    st.session_state.logs = ["📢 Initializing ADK 2.0 Runner & graph execution loop..."]
    st.session_state.events = []
    st.session_state.wf_output = None
    st.session_state.interrupted = False
    
    st.session_state.node_statuses = {
        "TriageNode": "pending",
        "MemoryNode": "pending",
        "RedactNode": "pending"
    }
    
    # Package input
    input_data = {"filename": doc_name, "raw_text": input_content}
    
    # Wrap in types.Content
    content = types.Content(
        role="user",
        parts=[types.Part(text=json.dumps(input_data))]
    )
    
    # Run the workflow using runner.run_async
    async for event in st.session_state.runner.run_async(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
        new_message=content
    ):
        process_event(event)
        # Sleep briefly to allow progress visualization
        await asyncio.sleep(0.6)

async def resume_workflow(approved: bool, edited_text: str, comments: str):
    st.session_state.logs.append("📢 Resuming workflow execution from human validation...")
    
    response_payload = {
        "approved": approved,
        "edited_text": edited_text,
        "comments": comments
    }
    
    # Package function response
    content = types.Content(
        role="user",
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    name="hitl_approval_response",
                    id=st.session_state.interrupt_id,
                    response=response_payload
                )
            )
        ]
    )
    
    st.session_state.interrupted = False
    
    async for event in st.session_state.runner.run_async(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
        new_message=content
    ):
        process_event(event)
        
        # Check if the final output was returned
        if event.output is not None and isinstance(event.output, dict) and event.output.get("status") in ["Approved", "Rejected"]:
            st.session_state.wf_output = event.output
            
        await asyncio.sleep(0.6)
# -----------------------------------------------------------------------------

# Handle triggers
if start_btn:
    doc_text = text_input
    doc_name = st.session_state.get("document_name", "Text Input")
    if uploaded_file is not None:
        doc_text = uploaded_file.read().decode("utf-8")
        doc_name = uploaded_file.name
        
    if not doc_text.strip():
        st.warning("Please upload a file or paste document content to start.")
    else:
        # Run async loop
        asyncio.run(drive_workflow(doc_text, doc_name))
        st.rerun()

# ----------------- Rendering Right Column (Visualization & Results) -----------------
with col2:
    st.markdown("#### 📊 Workflow Execution Graph Status")
    
    # Dynamic Stepper SVG/HTML Graph rendering
    def draw_visualization_graph():
        statuses = st.session_state.node_statuses
        active = st.session_state.active_node
        
        def get_class(node):
            status = statuses.get(node, "pending")
            if status == "completed":
                return "step-completed"
            elif status == "active":
                return "step-active"
            elif status == "interrupted":
                return "step-interrupted"
            return "step-pending"
            
        start_class = "step-completed" if active != "START" else "step-active"
        triage_class = get_class("TriageNode")
        memory_class = get_class("MemoryNode")
        redact_class = get_class("RedactNode")
        end_class = "step-completed" if statuses.get("RedactNode") == "completed" else "step-pending"
        
        html_code = f"""
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 1.5rem 0; flex-wrap: wrap;">
            <div class="step-box {start_class}">START<br><span style="font-size:9px;font-weight:normal;color:#aaa;">Document Submitted</span></div>
            <div style="color: #6c757d; font-size: 16px; font-weight: bold;">➔</div>
            <div class="step-box {triage_class}">TriageNode<br><span style="font-size:9px;font-weight:normal;">Governing / Liability / IP</span></div>
            <div style="color: #6c757d; font-size: 16px; font-weight: bold;">➔</div>
            <div class="step-box {memory_class}">MemoryNode<br><span style="font-size:9px;font-weight:normal;">State Precedents</span></div>
            <div style="color: #6c757d; font-size: 16px; font-weight: bold;">➔</div>
            <div class="step-box {redact_class}">RedactNode<br><span style="font-size:9px;font-weight:normal;">PII Redaction & HITL</span></div>
            <div style="color: #6c757d; font-size: 16px; font-weight: bold;">➔</div>
            <div class="step-box {end_class}">END<br><span style="font-size:9px;font-weight:normal;color:#aaa;">Finalized Output</span></div>
        </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)

    draw_visualization_graph()
    
    # Real-time console logs
    st.markdown("##### 📝 Execution Agent Logs")
    log_content = "\n".join(st.session_state.logs)
    st.text_area("Agent communication channel:", value=log_content, height=120, disabled=True)

    # Human-in-the-Loop review Panel
    if st.session_state.interrupted:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("### 🛑 Human-in-the-Loop compliance validation required!")
        st.markdown("Workflow is currently suspended at **RedactNode**. Please review the triaged conflicts and privacy redactions below.")
        
        payload = st.session_state.interrupted_payload
        
        # Display flagged conflicts
        st.markdown("#### 🚨 Flagged Compliance Conflicts")
        triaged = payload.get("triaged_clauses", [])
        if not triaged:
            st.success("No critical conflicting clauses flagged!")
        else:
            for idx, conflict in enumerate(triaged):
                severity_color = "🔴 High" if conflict["severity"] == "High" else "🟡 Medium"
                st.markdown(f"**{idx + 1}. {conflict['rule_name']}** (Severity: {severity_color})")
                st.caption(conflict["description"])
                for match in conflict["matches"]:
                    st.warning(f"Line {match['line_no']}: *\"{match['text']}\"* (Matched: `{match['pattern']}`) ")

        # Display Memory registry matches
        st.markdown("#### 🧠 Historical Compliance Matches")
        memory_matches = payload.get("memory_matches", [])
        if not memory_matches:
            st.info("No matching resolution precedent found in historical database.")
        else:
            for match in memory_matches:
                st.markdown(f"- **Matched Clause:** *\"{match['clause']}\"*")
                st.success(f"  💡 **Historical Resolution:** {match['historical_resolution']} *(Resolved on {match['resolved_date']})*")

        # Display PII Summary
        st.markdown("#### 🛡️ Privacy Redactions Summary")
        pii = payload.get("pii_summary", {})
        col_pii1, col_pii2, col_pii3 = st.columns(3)
        with col_pii1:
            st.metric("Emails Redacted", pii.get("emails", 0))
        with col_pii2:
            st.metric("Phones Redacted", pii.get("phones", 0))
        with col_pii3:
            st.metric("API Keys Redacted", pii.get("api_keys", 0))

        # Review & Edit redacted text
        st.markdown("#### ✏️ Redacted Document Preview & Edit")
        st.caption("You can manually adjust the redacted text before granting final approval.")
        edited_text = st.text_area("Preview draft document:", value=payload.get("redacted_text", ""), height=250, key="hitl_edited_text")
        
        comments = st.text_input("Review Comments / Amendment Notes", placeholder="e.g. Approved governing law change; PII verified.", key="hitl_comments")
        
        col_action1, col_action2 = st.columns(2)
        with col_action1:
            approve = st.button("✅ Approve & Redact", type="primary", use_container_width=True)
        with col_action2:
            reject = st.button("❌ Reject Document", use_container_width=True)
            
        if approve:
            asyncio.run(resume_workflow(True, st.session_state.hitl_edited_text, st.session_state.hitl_comments))
            st.rerun()
        elif reject:
            asyncio.run(resume_workflow(False, st.session_state.hitl_edited_text, st.session_state.hitl_comments))
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    # Approved/Final output display
    if st.session_state.wf_output is not None:
        status = st.session_state.wf_output.get("status", "")
        st.markdown('<div class="premium-card" style="border-color: #198754;">', unsafe_allow_html=True)
        if status == "Approved":
            st.success("### 🎉 Document Audited & Approved!")
            st.markdown(f"**Comments:** *\"{st.session_state.wf_output.get('comments', 'None')}\"*")
            
            # Show summary
            pii = st.session_state.wf_output.get("pii_redacted", {})
            st.markdown(f"**Security Summary:** Emails redacted: `{pii.get('emails', 0)}` | Phones redacted: `{pii.get('phones', 0)}` | Keys redacted: `{pii.get('api_keys', 0)}`")
            
            # Text output area
            st.text_area("Final Clean Document:", value=st.session_state.wf_output.get("redacted_text", ""), height=250)
            
            # Download button
            st.download_button(
                label="📥 Download Clean Document",
                data=st.session_state.wf_output.get("redacted_text", ""),
                file_name="clean_document.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.error("### ❌ Document Audited & Rejected")
            st.markdown(f"**Reason/Comments:** *\"{st.session_state.wf_output.get('comments', 'None')}\"*")
            st.warning("Please modify the original document input to resolve the compliance conflicts and re-submit.")
        st.markdown('</div>', unsafe_allow_html=True)
