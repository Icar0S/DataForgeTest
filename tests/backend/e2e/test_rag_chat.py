"""Test RAG chat system locally."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from rag.config_simple import RAGConfig
from rag.simple_rag import SimpleRAG
from rag.simple_chat import SimpleChatEngine


def test_rag_system():
    """Test the RAG system with a sample query."""

    print("=" * 70)
    print("🧪 TESTE DO SISTEMA RAG")
    print("=" * 70)

    # Initialize RAG system
    print("\n📚 Inicializando sistema RAG...")
    config = RAGConfig.from_env()
    rag_system = SimpleRAG(config)
    chat_engine = SimpleChatEngine(rag_system)

    print(f"   ✓ Documentos carregados: {len(rag_system.documents)}")

    # Count total chunks
    total_chunks = sum(len(chunks) for chunks in rag_system.document_chunks.values())
    print(f"   ✓ Chunks criados: {total_chunks}")

    if len(rag_system.documents) == 0:
        print("\n❌ Nenhum documento encontrado!")
        print("   Execute: python import_documents.py docs_to_import")
        return

    # Show sample documents
    print("\n📄 Documentos na base:")
    for i, (doc_id, doc_data) in enumerate(list(rag_system.documents.items())[:5]):
        filename = doc_data.get("metadata", {}).get("filename", "Unknown")
        content_len = len(doc_data.get("content", ""))
        print(f"   {i+1}. {filename} ({content_len} chars)")

    if len(rag_system.documents) > 5:
        print(f"   ... e mais {len(rag_system.documents) - 5} documentos")

    # Test search
    print("\n🔍 Testando busca...")
    test_query = "What are the best practices for Spark?"
    results = rag_system.search(test_query)

    print(f"   Query: '{test_query}'")
    print(f"   Resultados encontrados: {len(results)}")

    if results:
        print("\n📊 Top 3 resultados:")
        for i, result in enumerate(results[:3]):
            print(f"\n   {i+1}. Score: {result['score']:.4f}")
            print(f"      Fonte: {result['metadata'].get('filename', 'Unknown')}")
            print(f"      Texto: {result['text'][:150]}...")

    # Test chat
    print("\n💬 Testando chat engine...")
    chat_response = chat_engine.chat(test_query)

    print(f"\n   Resposta: {chat_response['response'][:200]}...")
    print(f"\n   Citações: {len(chat_response['citations'])}")

    for i, citation in enumerate(chat_response["citations"][:3]):
        print(f"\n   [{i+1}] {citation['metadata'].get('filename', 'Unknown')}")
        print(f"       {citation['text'][:100]}...")

    print("\n" + "=" * 70)
    print("✅ Teste concluído com sucesso!")
    print("=" * 70)


if __name__ == "__main__":
    test_rag_system()
