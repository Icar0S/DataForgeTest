"""Test direct RAG system to check if it loads the cleaned knowledge base."""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))


def test_rag_direct():
    """Test RAG system directly."""
    print("=" * 70)
    print("TESTING RAG SYSTEM DIRECTLY")
    print("=" * 70)

    try:
        from src.rag.simple_rag import SimpleRAG
        from src.rag.config_simple import RAGConfig
        from src.rag.simple_chat import SimpleChatEngine

        config = RAGConfig.from_env()
        rag = SimpleRAG(config)
        chat = SimpleChatEngine(rag)

        print(f"📚 Documents loaded: {len(rag.documents)}")

        if rag.documents:
            print("\n📋 Document samples:")
            for i, (doc_id, doc_data) in enumerate(list(rag.documents.items())[:3]):
                metadata = doc_data.get("metadata", {})
                filename = metadata.get("filename", "Unknown")
                content_length = len(doc_data.get("content", ""))
                print(f"   {i+1}. {filename} ({content_length} chars)")

        # Test a specific question
        print("\n🧪 Testing question: 'What is data quality testing?'")
        result = chat.chat("What is data quality testing?")

        response = result.get("response", "")
        citations = result.get("citations", [])

        print(f"📏 Response length: {len(response)}")
        print(f"📚 Citations: {len(citations)}")

        if "I don't have specific information" in response:
            print("❌ Getting generic response")
            print("🔍 This suggests the system is not finding relevant content")

            # Let's test the search directly
            print("\n🔍 Testing direct search:")
            search_results = rag.search("data quality testing", top_k=3)
            print(f"   Search results: {len(search_results)}")

            for i, result in enumerate(search_results[:2]):
                score = result.get("score", 0)
                text_preview = result.get("text", "")[:100]
                print(f"   {i+1}. Score: {score:.3f} - {text_preview}...")
        else:
            print("✅ Getting detailed response")
            print(f"📝 Preview: {response[:200]}...")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_rag_direct()
