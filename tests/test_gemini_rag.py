"""Test Gemini with RAG - Simple quick test."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Configure Gemini
os.environ["LLM_PROVIDER"] = "gemini"
if "GEMINI_API_KEY" not in os.environ:
    raise ValueError("GEMINI_API_KEY environment variable is required")
os.environ["GEMINI_MODEL"] = "gemini-2.5-flash-lite"

from rag.config_simple import RAGConfig  # type: ignore  # noqa: E402
from rag.simple_rag import SimpleRAG  # type: ignore  # noqa: E402
from rag.simple_chat import SimpleChatEngine  # type: ignore  # noqa: E402

print("🤖 Testando Chat com RAG + Gemini...\n")

# Initialize
config = RAGConfig.from_env()
rag = SimpleRAG(config)
chat = SimpleChatEngine(rag)

print(f"📚 Documentos: {len(rag.documents)}")
print(f"🧠 LLM: {'Ativo' if chat.use_llm else 'Fallback'}")
print(f"   Provider: {os.getenv('LLM_PROVIDER')}")
print(f"   Model: {os.getenv('GEMINI_MODEL')}\n")

# Test question
question = "What is PySpark?"
print(f"❓ Pergunta: {question}\n")

result = chat.chat(question)

print("💬 Resposta:")
print(result["response"])
print(f"\n📎 Citações: {len(result['citations'])}")

# Check if it's template or real LLM
is_template = "based on the documentation" in result["response"].lower()
print(f"\n{'✅' if not is_template else '❌'} Usando LLM: {not is_template}")
