import os
import re
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from google.adk import Workflow
from google.adk.workflow import node, START, Edge
from google.adk.events import RequestInput

from compliance_analyzer.tools import SecureStreamReader
from compliance_analyzer.config import COMPLIANCE_RULES

# 1. State Schema Definition
class ComplianceState(BaseModel):
    document_name: str = ""
    raw_text: str = ""
    triaged_clauses: List[Dict[str, Any]] = Field(default_factory=list)
    memory_matches: List[Dict[str, Any]] = Field(default_factory=list)
    redacted_text: str = ""
    compliance_status: str = "Pending"  # "Pending", "Triaged", "Checked", "Approved", "Rejected"
    interrupted_node: Optional[str] = None
    hitl_decision: Optional[Dict[str, Any]] = None


# 2. TriageNode Definition
@node(name="TriageNode", rerun_on_resume=True)
async def triage_node(ctx, node_input: Any):
    """Extracts text, parses it, and flags conflicting clauses based on a configuration file."""
    print(f"DEBUG: triage_node received node_input={node_input} of type={type(node_input)}")
    
    # Unpack google.genai.types.Content or similar object if passed as node input
    if hasattr(node_input, "parts") and node_input.parts:
        part_text = node_input.parts[0].text
        try:
            parsed = json.loads(part_text)
            if isinstance(parsed, dict):
                node_input = parsed
        except Exception:
            node_input = part_text

    filename = ""
    raw_text = ""
    
    if isinstance(node_input, dict):
        filename = node_input.get("filename", "")
        raw_text = node_input.get("raw_text", "")
    elif isinstance(node_input, str):
        if node_input.endswith(('.txt', '.json', '.md')):
            filename = node_input
        else:
            raw_text = node_input

    # Extract text using SecureStreamReader if a filename is provided
    if filename:
        workspace_dir = os.path.abspath(os.getcwd())
        reader = SecureStreamReader(workspace_dir)
        try:
            raw_text = reader.read_text_file(filename)
        except Exception as e:
            raw_text = f"Error reading file: {str(e)}"
            
    # Update context state
    ctx.state["document_name"] = filename or "Text Input"
    ctx.state["raw_text"] = raw_text
    
    # Flag conflicting clauses
    flagged = []
    lines = raw_text.splitlines()
    for rule in COMPLIANCE_RULES["conflicting_clauses"]:
        matched_lines = []
        for i, line in enumerate(lines):
            for pattern in rule["patterns"]:
                if re.search(r'\b' + re.escape(pattern) + r'\b', line, re.IGNORECASE):
                    matched_lines.append({
                        "line_no": i + 1,
                        "text": line.strip(),
                        "pattern": pattern
                    })
        
        # If we have multiple matches, flag it as a potential conflict
        if len(matched_lines) >= 2 or (len(matched_lines) >= 1 and rule["id"] == "governing_law_conflict"):
            flagged.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "description": rule["description"],
                "matches": matched_lines,
                "severity": rule["severity"]
            })
            
    ctx.state["triaged_clauses"] = flagged
    ctx.state["compliance_status"] = "Triaged"
    
    return {"status": "success", "triaged_clauses": flagged}


# 3. MemoryNode Definition
@node(name="MemoryNode", rerun_on_resume=True)
async def memory_node(ctx, node_input: Any):
    """Simulates a long-term state registry checking for previously flagged compliance patterns."""
    workspace_dir = os.path.abspath(os.getcwd())
    reader = SecureStreamReader(workspace_dir)
    registry_file = "compliance_registry.json"
    
    # Load historical compliance registry
    registry = []
    if os.path.exists(os.path.join(workspace_dir, registry_file)):
        try:
            registry = reader.read_json_file(registry_file)
        except Exception:
            registry = []
    else:
        # Seed the registry with mock historical resolutions
        registry = [
            {
                "rule_id": "governing_law_conflict",
                "matched_text": "governing law is the State of California",
                "resolution": "Amended to California only to resolve conflict with New York clause.",
                "resolved_date": "2026-05-10"
            },
            {
                "rule_id": "ip_ownership_conflict",
                "matched_text": "jointly owned by both parties",
                "resolution": "Approved after adjusting contract terms to joint licensing.",
                "resolved_date": "2026-06-01"
            }
        ]
        try:
            reader.write_json_file(registry_file, registry)
        except Exception:
            pass

    triaged_clauses = ctx.state.get("triaged_clauses", [])
    memory_matches = []
    
    # Check current triaged clauses against historical ones in the registry
    for clause in triaged_clauses:
        for match in clause.get("matches", []):
            match_text = match["text"].lower()
            for entry in registry:
                if entry["matched_text"].lower() in match_text or match_text in entry["matched_text"].lower():
                    memory_matches.append({
                        "clause": match["text"],
                        "historical_resolution": entry["resolution"],
                        "resolved_date": entry["resolved_date"],
                        "rule_id": entry["rule_id"]
                    })
                    
    ctx.state["memory_matches"] = memory_matches
    ctx.state["compliance_status"] = "Checked"
    
    return {"status": "success", "memory_matches": memory_matches}


# 4. RedactNode Definition (handles Human-in-the-Loop)
@node(name="RedactNode", rerun_on_resume=True)
async def redact_node(ctx, node_input: Any):
    """Reviews draft output for security compliance, automatically redacting PII, and handles HITL approval."""
    raw_text = ctx.state.get("raw_text", "")
    triaged_clauses = ctx.state.get("triaged_clauses", [])
    memory_matches = ctx.state.get("memory_matches", [])
    
    # Redact raw PII
    redacted_text = raw_text
    
    # Redact Emails
    email_pattern = COMPLIANCE_RULES["pii_patterns"]["email"]
    emails_found = re.findall(email_pattern, redacted_text)
    redacted_text = re.sub(email_pattern, "[REDACTED_EMAIL]", redacted_text)
    
    # Redact Phones
    phone_pattern = COMPLIANCE_RULES["pii_patterns"]["phone"]
    phones_found = re.findall(phone_pattern, redacted_text)
    redacted_text = re.sub(phone_pattern, "[REDACTED_PHONE]", redacted_text)
    
    # Redact API Keys
    api_key_pattern = COMPLIANCE_RULES["pii_patterns"]["api_key"]
    api_keys_found = re.findall(api_key_pattern, redacted_text)
    redacted_text = re.sub(api_key_pattern, "[REDACTED_API_KEY]", redacted_text)
    
    ctx.state["redacted_text"] = redacted_text
    
    pii_summary = {
        "emails": len(emails_found),
        "phones": len(phones_found),
        "api_keys": len(api_keys_found)
    }
    
    interrupt_id = f"hitl_approval:{ctx.node_path}"
    
    # Check if we are resuming from an interrupt
    if interrupt_id in ctx.resume_inputs:
        decision = ctx.resume_inputs[interrupt_id]
        ctx.state["hitl_decision"] = decision
        ctx.state["interrupted_node"] = None
        
        approved = decision.get("approved", False)
        edited_text = decision.get("edited_text", redacted_text)
        
        if approved:
            ctx.state["compliance_status"] = "Approved"
            ctx.state["redacted_text"] = edited_text
            
            # Save the final redacted document
            workspace_dir = os.path.abspath(os.getcwd())
            reader = SecureStreamReader(workspace_dir)
            doc_name = ctx.state.get("document_name", "output.txt")
            if not doc_name or doc_name == "Text Input":
                doc_name = "analyzed_document.txt"
            base, ext = os.path.splitext(doc_name)
            output_filename = f"{base}_redacted{ext}"
            try:
                reader.write_text_file(output_filename, edited_text)
            except Exception:
                pass
                
            yield {
                "status": "Approved",
                "redacted_text": edited_text,
                "pii_redacted": pii_summary,
                "comments": decision.get("comments", "")
            }
            return
        else:
            ctx.state["compliance_status"] = "Rejected"
            yield {
                "status": "Rejected",
                "redacted_text": redacted_text,
                "pii_redacted": pii_summary,
                "comments": decision.get("comments", "")
            }
            return
    else:
        # Request Human-in-the-Loop review & redact approval
        ctx.state["interrupted_node"] = "RedactNode"
        yield RequestInput(
            interrupt_id=interrupt_id,
            message="Please review the document, approve the redaction, and resolve compliance flags.",
            payload={
                "redacted_text": redacted_text,
                "triaged_clauses": triaged_clauses,
                "memory_matches": memory_matches,
                "pii_summary": pii_summary
            }
        )


# 5. Workflow Composition
compliance_workflow = Workflow(
    name="compliance_workflow",
    description="Document Compliance and Privacy Analyzer Workflow",
    edges=[
        Edge(from_node=START, to_node=triage_node),
        Edge(from_node=triage_node, to_node=memory_node),
        Edge(from_node=memory_node, to_node=redact_node)
    ],
    state_schema=ComplianceState
)
