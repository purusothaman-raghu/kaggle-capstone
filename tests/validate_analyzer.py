import asyncio
import os
import json
import sys

# Resolve project root dynamically
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from compliance_analyzer.agents import compliance_workflow
from google.genai import types

async def run_validation(filename: str):
    print(f"\n==================================================")
    print(f"[*] Testing Document: {filename}")
    print(f"==================================================")
    
    session_service = InMemorySessionService()
    runner = Runner(
        session_service=session_service,
        agent=compliance_workflow,
        app_name="compliance_analyzer",
        auto_create_session=True
    )
    
    input_data = {"filename": filename, "raw_text": ""}
    content = types.Content(
        role="user",
        parts=[types.Part(text=json.dumps(input_data))]
    )
    
    interrupt_id = None
    payload = None
    
    # Stage 1: Initial run
    async for event in runner.run_async(
        user_id="validator",
        session_id=f"session_{filename.replace('.', '_')}",
        new_message=content
    ):
        path = event.node_info.path if event.node_info else "System"
        print(f"-> Event yielded from: {path}")
        if event.long_running_tool_ids:
            interrupt_id = list(event.long_running_tool_ids)[0]
            fc = event.content.parts[0].function_call
            payload = fc.args.get("payload", {})
            print(f"  [PAUSED] Interrupt ID: {interrupt_id}")
            
    # Print triage and memory reports
    if payload:
        print("\n[TRIAGE] Conflicts Flagged:")
        for idx, conflict in enumerate(payload.get("triaged_clauses", [])):
            print(f"   - {conflict['rule_name']} ({conflict['severity']})")
            
        print("\n[MEMORY] Registry Matches:")
        for idx, match in enumerate(payload.get("memory_matches", [])):
            print(f"   - Historical Resolution found for: \"{match['clause'][:50]}...\"")
            
        print("\n[PII] Redactions:")
        pii = payload.get("pii_summary", {})
        print(f"   - Emails redacted: {pii.get('emails', 0)}")
        print(f"   - Phones redacted: {pii.get('phones', 0)}")
        print(f"   - API Keys redacted: {pii.get('api_keys', 0)}")
        
        # Stage 2: Resume with approval
        print("\n[HITL] Sending Human approval response...")
        resume_payload = {
            "approved": True,
            "edited_text": payload.get("redacted_text", ""),
            "comments": "Automated validation approve."
        }
        resume_message = types.Content(
            role="user",
            parts=[
                types.Part(
                    function_response=types.FunctionResponse(
                        name="hitl_approval_response",
                        id=interrupt_id,
                        response=resume_payload
                    )
                )
            ]
        )
        
        final_output = None
        async for event in runner.run_async(
            user_id="validator",
            session_id=f"session_{filename.replace('.', '_')}",
            new_message=resume_message
        ):
            path = event.node_info.path if event.node_info else "System"
            print(f"-> Event yielded from: {path}")
            if event.output is not None and not event.long_running_tool_ids:
                final_output = event.output
                
        if final_output:
            print(f"\n[SUCCESS] Audited Document saved successfully!")
            print(f"   - Status: {final_output.get('status')}")
            print(f"   - Comments: {final_output.get('comments')}")
            
            # Check if redacted file is generated
            base, ext = os.path.splitext(filename)
            redacted_filename = f"{base}_redacted{ext}"
            redacted_filepath = os.path.join(PROJECT_ROOT, redacted_filename)
            if os.path.exists(redacted_filepath):
                print(f"   - Redacted File exists: {redacted_filename} ({os.path.getsize(redacted_filepath)} bytes)")
            else:
                print(f"   - Error: Redacted file not found!")
    else:
        print("[-] Error: Workflow did not interrupt.")

async def main():
    os.chdir(PROJECT_ROOT)
    await run_validation("NonDisclosureAgreement.txt")
    await run_validation("ConsultingAgreement.txt")

if __name__ == "__main__":
    asyncio.run(main())
