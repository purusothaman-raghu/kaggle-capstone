import sys
import os

# Resolve project root dynamically
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Import the mcp server module
from compliance_analyzer.mcp_server import list_workspace_documents, read_document_stream, write_document_stream

def test_mcp_tools():
    print("==================================================")
    print("[*] Testing MCP Server Tools")
    print("==================================================")
    
    # 1. Test listing workspace documents
    print("\n1. Testing 'list_workspace_documents'...")
    try:
        files = list_workspace_documents()
        print("[SUCCESS] Files found in workspace:")
        for f in files:
            print(f"   - {f}")
    except Exception as e:
        print(f"[FAILED] list_workspace_documents raised: {str(e)}")
        
    # 2. Test reading a document stream securely
    print("\n2. Testing 'read_document_stream'...")
    try:
        content = read_document_stream("NonDisclosureAgreement.txt")
        if "Non-Disclosure Agreement" in content:
            print(f"[SUCCESS] Read document stream successfully. Character count: {len(content)}")
        else:
            print(f"[FAILED] Content did not match expected NDA content. Length: {len(content)}")
    except Exception as e:
        print(f"[FAILED] read_document_stream raised: {str(e)}")
        
    # 3. Test writing a document stream securely
    print("\n3. Testing 'write_document_stream'...")
    test_file = "mcp_test_output.txt"
    test_content = "Model Context Protocol Secure Tool stream test message."
    try:
        result = write_document_stream(test_file, test_content)
        print(f"[SUCCESS] Result: {result}")
        
        # Verify by reading back
        verify_content = read_document_stream(test_file)
        if verify_content == test_content:
            print("[SUCCESS] Verified written content successfully.")
        else:
            print(f"[FAILED] Written content mismatch. Expected: '{test_content}', Got: '{verify_content}'")
            
        # Clean up
        filepath = os.path.join(PROJECT_ROOT, test_file)
        if os.path.exists(filepath):
            os.remove(filepath)
            print("[CLEANUP] Removed temporary test file.")
            
    except Exception as e:
        print(f"[FAILED] write_document_stream raised: {str(e)}")

if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    test_mcp_tools()
