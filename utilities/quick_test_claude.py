"""Quick test of Claude integration with RAG."""

import sys
import os

sys.path.insert(0, "src")

from rag.config_simple import RAGConfig
from rag.simple_rag import SimpleRAG
from rag.simple_chat import SimpleChatEngine

# Load RAG system
config = RAGConfig.from_env()
rag = SimpleRAG(config)

print(f"📚 Documentos: {len(rag.documents)}")
print(f"📦 Chunks: {sum(len(c) for c in rag.document_chunks.values())}")

# Test chat
chat = SimpleChatEngine(rag)
result = chat.chat("What are best practices for Spark?")

print(f"\n💬 Pergunta: What are best practices for Spark?")
print(f"\n📝 Resposta ({len(result['response'])} chars):")
print(result["response"][:500])
print(f"\n📚 Citações: {len(result['citations'])}")
