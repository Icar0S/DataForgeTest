"""Simplified RAG system diagnostics."""

import sys
import os
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def check_rag_system():
    """Simple check of RAG system components."""
    print("=" * 70)
    print("RAG SYSTEM QUICK DIAGNOSTICS")
    print("=" * 70)

    # 1. Check .env file
    print("\n1. ENVIRONMENT:")
    env_file = Path(".env")
    if env_file.exists():
        print("✓ .env file exists")
        with open(env_file) as f:
            content = f.read()
            if "LLM_API_KEY=" in content and "LLM_API_KEY=\n" not in content:
                print("✓ LLM_API_KEY is set")
            else:
                print("⚠ LLM_API_KEY is empty (using Simple RAG)")
    else:
        print("⚠ .env file not found")

    # 2. Check core imports
    print("\n2. CORE MODULES:")
    try:
        from src.rag.simple_rag import SimpleRAG
        from src.rag.simple_chat import SimpleChatEngine
        from src.rag.config_simple import RAGConfig

        print("✓ RAG modules import OK")
    except Exception as e:
        print(f"✗ RAG modules failed: {e}")
        return False

    # 3. Test basic functionality
    print("\n3. FUNCTIONALITY TEST:")
    try:
        config = RAGConfig.from_env()
        rag = SimpleRAG(config)
        chat = SimpleChatEngine(rag)

        # Add test document
        doc_id = rag.add_document(
            "Test document about data quality", {"filename": "test.txt"}
        )
        print(f"✓ Document added: {doc_id[:8]}...")

        # Test search
        results = rag.search("data quality")
        print(f"✓ Search works: {len(results)} results")

        # Test chat
        response = chat.chat("What is data quality?")
        if response and "response" in response:
            print(f"✓ Chat works: {len(response['response'])} chars")
        else:
            print("⚠ Chat response format unexpected")

    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False

    # 4. Check API
    print("\n4. API CHECK:")
    api_file = Path("src/api.py")
    if api_file.exists():
        print("✓ api.py exists")
        with open(api_file) as f:
            content = f.read()
            if "rag_bp" in content:
                print("✓ RAG blueprint registered")
            else:
                print("⚠ RAG blueprint unclear")
    else:
        print("✗ api.py not found")

    # 5. Check frontend
    print("\n5. FRONTEND CHECK:")
    chat_window = Path("frontend/frontend/src/components/ChatWindow.js")
    if chat_window.exists():
        print("✓ ChatWindow.js exists")
        with open(chat_window) as f:
            content = f.read()
            if "/api/rag/chat" in content:
                print("✓ Calls RAG API")
            else:
                print("⚠ RAG API call unclear")
    else:
        print("⚠ ChatWindow.js not found")

    print("\n" + "=" * 70)
    print("SUMMARY: RAG system appears to be working!")
    print("- Using Simple RAG (keyword-based search)")
    print("- To use Claude LLM: add LLM_API_KEY to .env")
    print("=" * 70)

    return True


if __name__ == "__main__":
    check_rag_system()
