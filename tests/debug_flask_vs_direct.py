"""Debug script to test Flask RAG vs Direct RAG."""

import requests
import json


def debug_flask_vs_direct():
    """Compare Flask RAG with Direct RAG to find the issue."""
    print("=" * 70)
    print("DEBUGGING FLASK RAG vs DIRECT RAG")
    print("=" * 70)

    # Test Direct RAG first
    print("\n🔬 TESTING DIRECT RAG:")
    try:
        import sys
        import os

        sys.path.insert(0, os.path.abspath("."))
        sys.path.insert(0, os.path.abspath("src"))

        from src.rag.simple_rag import SimpleRAG
        from src.rag.config_simple import RAGConfig
        from src.rag.simple_chat import SimpleChatEngine

        config = RAGConfig.from_env()
        rag = SimpleRAG(config)
        chat = SimpleChatEngine(rag)

        print(f"   📚 Documents: {len(rag.documents)}")
        print(f"   🔍 Chunks: {len(rag.document_chunks)}")

        # Test direct search
        search_results = rag.search("data quality", top_k=3)
        print(f"   🎯 Search results: {len(search_results)}")

        if search_results:
            print(f"   ✅ Direct RAG search working")
            # Test chat
            result = chat.chat("What is data quality?")
            response_length = len(result.get("response", ""))
            citations_count = len(result.get("citations", []))
            print(f"   💬 Direct chat response: {response_length} chars")
            print(f"   📚 Direct chat citations: {citations_count}")
        else:
            print(f"   ❌ Direct RAG search not working")

    except Exception as e:
        print(f"   ❌ Direct RAG failed: {e}")

    # Test Flask RAG
    print(f"\n🌐 TESTING FLASK RAG:")
    try:
        # Test simple question
        response = requests.post(
            "http://localhost:5000/api/rag/chat",
            json={"message": "data quality"},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )

        if response.status_code == 200:
            data = response.json()
            flask_response = data.get("response", "")
            flask_citations = data.get("citations", [])

            print(f"   💬 Flask response length: {len(flask_response)}")
            print(f"   📚 Flask citations: {len(flask_citations)}")
            print(f"   📝 Flask response preview: {flask_response[:100]}...")

            if "I don't have specific information" in flask_response:
                print(f"   ❌ Flask RAG giving generic responses")
                print(
                    f"   ❗ This indicates Flask RAG instance is not loading chunks properly"
                )
            else:
                print(f"   ✅ Flask RAG giving detailed responses")
        else:
            print(f"   ❌ Flask request failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Flask RAG failed: {e}")

    print(f"\n" + "=" * 70)
    print("🔍 DIAGNOSIS:")
    print("If Direct RAG works but Flask RAG doesn't,")
    print("the backend needs a proper restart to reload chunks.")
    print("Try: taskkill /f /im python.exe && cd src && python api.py")
    print("=" * 70)


if __name__ == "__main__":
    debug_flask_vs_direct()
