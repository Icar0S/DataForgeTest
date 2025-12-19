"""Test real chat with RAG using Ollama."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Configure Ollama
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "qwen2.5-coder:7b"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

from rag.config_simple import RAGConfig  # type: ignore  # noqa: E402
from rag.simple_rag import SimpleRAG  # type: ignore  # noqa: E402
from rag.simple_chat import SimpleChatEngine  # type: ignore  # noqa: E402

print("🤖 Iniciando chatbot com RAG e Ollama...\n")

# Initialize
config = RAGConfig.from_env()
rag = SimpleRAG(config)
chat = SimpleChatEngine(rag)

print(f"📚 Documentos carregados: {len(rag.documents)}")
print(f"🧠 LLM: {os.environ.get('LLM_PROVIDER')} - {os.environ.get('LLM_MODEL')}")
print(f"✨ Chat engine ready: {'LLM ativo' if chat.use_llm else 'Usando fallback'}\n")

# Test queries
test_queries = [
    "What is PySpark?",
    "How do I validate data quality?",
    "What are best practices for performance testing?",
]

for i, query in enumerate(test_queries, 1):
    print("=" * 70)
    print(f"🔸 Query {i}: {query}")
    print("=" * 70)

    result = chat.chat(query)

    print("\n💬 Resposta:")
    print(f"{result['response']}\n")

    print(f"📎 Citações ({len(result['citations'])}):")
    for j, citation in enumerate(result["citations"], 1):
        title = citation.get("title", citation.get("source", "Unknown"))
        score = citation.get("score", 0.0)
        print(f"   {j}. {title} (score: {score:.3f})")

    print()

print("=" * 70)
print("✅ Teste completo!")
print("=" * 70)
