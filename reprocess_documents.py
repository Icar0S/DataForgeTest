"""Reprocess documents to create chunks."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rag.config_simple import RAGConfig
from rag.simple_rag import SimpleRAG
import json
from pathlib import Path


def reprocess_documents():
    """Reprocess all documents to create chunks."""

    print("=" * 70)
    print("🔧 REPROCESSANDO DOCUMENTOS PARA CRIAR CHUNKS")
    print("=" * 70)

    # Load config
    config = RAGConfig.from_env()
    storage_path = Path(config.storage_path)
    docs_file = storage_path / "documents.json"

    if not docs_file.exists():
        print("\n❌ Arquivo documents.json não encontrado!")
        print("   Execute: python import_documents.py docs_to_import")
        return

    # Load existing documents
    with open(docs_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        documents = data.get("documents", {})

    print(f"\n📚 Encontrados {len(documents)} documentos")

    # Create RAG system
    rag = SimpleRAG(config)

    # Clear existing chunks
    rag.document_chunks = {}

    # Process each document
    print("\n🔄 Criando chunks...")
    total_chunks = 0

    for doc_id, doc_data in documents.items():
        content = doc_data.get("content", "")
        if not content:
            print(f"   ⚠️  Documento {doc_id[:8]} sem conteúdo, pulando...")
            continue

        # Create chunks for this document
        chunks = rag._create_chunks(content)
        rag.document_chunks[doc_id] = chunks
        total_chunks += len(chunks)

        filename = doc_data.get("metadata", {}).get("filename", "Unknown")
        print(f"   ✓ {filename}: {len(chunks)} chunks")

    # Save back to storage
    print(f"\n💾 Salvando {total_chunks} chunks no total...")
    rag.documents = documents  # Restore original documents
    rag._save_documents()

    print("\n" + "=" * 70)
    print(f"✅ Processamento concluído!")
    print(f"   📄 Documentos: {len(documents)}")
    print(f"   📦 Chunks: {total_chunks}")
    print("=" * 70)


if __name__ == "__main__":
    reprocess_documents()
