import sys
import os
import json
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from compliance_analyzer.agents import compliance_workflow
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def main():
    runner = Runner(
        session_service=InMemorySessionService(),
        agent=compliance_workflow,
        app_name="test_reporter",
        auto_create_session=True
    )
    
    # Read NDA
    with open("NonDisclosureAgreement.txt", "r", encoding="utf-8") as f:
        text = f.read()
        
    input_data = {"filename": "NonDisclosureAgreement.txt", "raw_text": text}
    content = types.Content(
        role="user",
        parts=[types.Part(text=json.dumps(input_data))]
    )
    
    payload = {}
    async for event in runner.run_async(user_id="user_test", session_id="session_test", new_message=content):
        if event.long_running_tool_ids:
            fc = event.content.parts[0].function_call
            payload = fc.args.get("payload", {})
            break
            
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Compliance Audit Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; color: #333; }}
        h1 {{ color: #0d6efd; }}
        .conflict {{ background: #fff; border-left: 4px solid #dc3545; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .conflict.Medium {{ border-left-color: #ffc107; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffe69c; color: #664d03; padding: 10px; margin-top: 10px; border-radius: 4px; }}
        .severity {{ font-weight: bold; text-transform: uppercase; }}
        .High {{ color: #dc3545; }}
        .Medium {{ color: #ffc107; }}
    </style>
</head>
<body>
    <h1>Document Compliance Audit Report</h1>
    <p><strong>Document:</strong> NonDisclosureAgreement.txt</p>
    <h2>Flagged Compliance Conflicts</h2>
    """
    
    triaged = payload.get("triaged_clauses", [])
    if not triaged:
        html += "<p>No conflicts flagged.</p>"
    else:
        for conflict in triaged:
            severity = conflict["severity"]
            html += f"""
            <div class="conflict {severity}">
                <h3>{conflict['rule_name']} (Severity: <span class="severity {severity}">{severity}</span>)</h3>
                <p><em>{conflict['description']}</em></p>
            """
            for match in conflict["matches"]:
                html += f"""
                <div class="warning">
                    <strong>Line {match['line_no']}:</strong> "{match['text']}"<br>
                    <strong>Matched patterns:</strong> <code>{match['pattern']}</code>
                </div>
                """
            html += "</div>"
            
    html += """
</body>
</html>
"""
    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Report generated: test_report.html")

if __name__ == "__main__":
    asyncio.run(main())
