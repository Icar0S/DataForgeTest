"""Fix RAG system by rebuilding chunks for existing documents."""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


def rebuild_rag_chunks():
    """Rebuild chunks for all documents in the RAG system."""
    print("=" * 70)
    print("REBUILDING RAG CHUNKS")
    print("=" * 70)

    try:
        from rag.simple_rag import SimpleRAG
        from rag.config_simple import RAGConfig

        config = RAGConfig.from_env()
        rag = SimpleRAG(config)

        print(f"📚 Documents loaded: {len(rag.documents)}")
        print(f"🔍 Chunks loaded: {len(rag.document_chunks)}")

        if len(rag.document_chunks) == 0:
            print("\n⚠️  No chunks found! Rebuilding chunks for all documents...")

            # Rebuild chunks for all documents
            for doc_id, doc_data in rag.documents.items():
                content = doc_data.get("content", "")
                if content:
                    chunks = rag._create_chunks(content)
                    rag.document_chunks[doc_id] = chunks

                    filename = doc_data.get("metadata", {}).get("filename", "Unknown")
                    print(f"   ✅ Created {len(chunks)} chunks for {filename}")

            # Save the updated structure
            rag._save_documents()
            print(f"\n💾 Chunks saved to storage")

            print(f"\n📊 FINAL STATS:")
            print(f"   Documents: {len(rag.documents)}")
            print(f"   Chunks: {len(rag.document_chunks)}")

            # Test search after rebuilding
            print(f"\n🧪 Testing search after rebuild:")
            search_results = rag.search("data quality testing", top_k=3)
            print(f"   Search results: {len(search_results)}")

            if search_results:
                for i, result in enumerate(search_results[:2]):
                    score = result.get("score", 0)
                    text_preview = result.get("text", "")[:80]
                    print(f"   {i+1}. Score: {score:.3f} - {text_preview}...")

                print(f"\n✅ RAG system fixed! Search is now working.")
            else:
                print(f"\n❌ Search still not working after rebuild.")
        else:
            print("\n✅ Chunks already exist, no rebuild needed.")

            # Test current search
            print(f"\n🧪 Testing current search:")
            search_results = rag.search("data quality testing", top_k=3)
            print(f"   Search results: {len(search_results)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    rebuild_rag_chunks()
