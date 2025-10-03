"""Debug script to check RAG configuration and file loading."""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath("."))


def debug_config():
    """Debug the RAG configuration."""
    print("=" * 70)
    print("DEBUGGING RAG CONFIGURATION")
    print("=" * 70)

    # Test current working directory
    print(f"Current working directory: {os.getcwd()}")

    # Test different path configurations
    paths_to_test = [
        "./storage/vectorstore",
        "../storage/vectorstore",
        "storage/vectorstore",
        os.path.join(os.path.dirname(__file__), "storage/vectorstore"),
        os.path.join(os.path.dirname(__file__), "../storage/vectorstore"),
    ]

    for path_str in paths_to_test:
        path = Path(path_str)
        docs_file = path / "documents.json"

        print(f"\n📁 Testing path: {path_str}")
        print(f"   Resolved to: {path.resolve()}")
        print(f"   Exists: {path.exists()}")
        print(f"   documents.json exists: {docs_file.exists()}")

        if docs_file.exists():
            try:
                import json

                with open(docs_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                documents = data.get("documents", {})
                print(f"   ✅ Successfully loaded {len(documents)} documents")
                return path_str
            except Exception as e:
                print(f"   ❌ Error loading: {e}")

    return None


def test_rag_with_working_path():
    """Test RAG with the working path."""
    working_path = debug_config()

    if working_path:
        print(f"\n" + "=" * 70)
        print(f"TESTING RAG WITH WORKING PATH: {working_path}")
        print("=" * 70)

        try:
            sys.path.insert(0, "src")
            from rag.simple_rag import SimpleRAG
            from rag.config_simple import RAGConfig
            from rag.simple_chat import SimpleChatEngine

            # Create custom config with working path
            config = RAGConfig()
            config.storage_path = Path(working_path)

            rag = SimpleRAG(config)
            chat = SimpleChatEngine(rag)

            print(f"📚 Documents loaded: {len(rag.documents)}")
            print(f"🔍 Chunks loaded: {len(rag.document_chunks)}")

            if len(rag.documents) > 0:
                print("✅ RAG loaded successfully!")

                # Test search
                results = rag.search("data quality", top_k=3)
                print(f"🎯 Search results: {len(results)}")

                if results:
                    # Test chat
                    response = chat.chat("What is data quality testing?")
                    print(
                        f"💬 Chat response length: {len(response.get('response', ''))}"
                    )
                    print(f"📚 Citations: {len(response.get('citations', []))}")
                else:
                    print("❌ Search not working")
            else:
                print("❌ No documents loaded")

        except Exception as e:
            print(f"❌ Error testing RAG: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_rag_with_working_path()
