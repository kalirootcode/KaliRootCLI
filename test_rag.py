import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kalirootcli.rag_engine import KnowledgeBase

def test_rag():
    rag = KnowledgeBase()
    
    # Test Query
    query = "Nmap scan results: Port 80 is open running Apache 2.4.49. Also running OpenSSH 7.2p2."
    print(f"Query: {query}\n")
    
    print("Testing RAG extraction and retrieval...")
    context = rag.get_context(query)
    
    print("-" * 50)
    print("GENERATED RAG CONTEXT:")
    print("-" * 50)
    print(context)
    print("-" * 50)
    
    if "CVE-" in context:
        print("✅ SUCCESS: CVEs found and injected.")
    else:
        print("❌ FAILURE: No CVEs found (Check network or extraction regex).")

if __name__ == "__main__":
    test_rag()
