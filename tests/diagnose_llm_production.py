"""Diagnostic test to check LLM initialization in production-like environment."""

import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("=" * 70)
print("🔍 DIAGNÓSTICO: LLM INITIALIZATION")
print("=" * 70)

# Simulate production environment
print("\n📋 Cenário 1: Produção SEM variáveis configuradas")
print("-" * 70)
# Clear all LLM-related env vars
for key in os.environ.keys():
    if "LLM" in key or "OLLAMA" in key or "GEMINI" in key or "ANTHROPIC" in key:
        del os.environ[key]

from llm_client import get_default_llm_client  # type: ignore  # noqa: E402

client = get_default_llm_client()
print(f"Result: {client}")
print(f"use_llm would be: {client is not None}")

# Simulate production WITH Gemini configured but no package
print("\n\n📋 Cenário 2: Produção COM Gemini configurado (mas sem pacote)")
print("-" * 70)
os.environ["LLM_PROVIDER"] = "gemini"
os.environ["GEMINI_API_KEY"] = "fake-key-for-testing"
os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"

# Reload module to test again
import llm_client as llm_module  # type: ignore  # noqa: E402

importlib.reload(llm_module)
from llm_client import get_default_llm_client as get_client2  # type: ignore  # noqa: E402

client2 = get_client2()
print(f"Result: {client2}")
print(f"use_llm would be: {client2 is not None}")

# Simulate production WITH Ollama (will fail - no localhost:11434)
print("\n\n📋 Cenário 3: Produção COM Ollama configurado (localhost não existe)")
print("-" * 70)
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "qwen2.5-coder:7b"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

importlib.reload(llm_module)
from llm_client import get_default_llm_client as get_client3  # type: ignore  # noqa: E402

client3 = get_client3()
print(f"Result: {client3}")
print(f"use_llm would be: {client3 is not None}")

# Check RAG integration
print("\n\n📋 Cenário 4: RAG Chat Engine Initialization")
print("-" * 70)

# Test with Ollama (should fail in production)
os.environ["LLM_PROVIDER"] = "ollama"
from rag.config_simple import RAGConfig  # type: ignore  # noqa: E402
from rag.simple_rag import SimpleRAG  # type: ignore  # noqa: E402
from rag.simple_chat import SimpleChatEngine  # type: ignore  # noqa: E402

config = RAGConfig.from_env()
rag = SimpleRAG(config)
chat = SimpleChatEngine(rag)

print("\nRAG Chat Status:")
print(f"  - llm_client: {chat.llm_client}")
print(f"  - use_llm: {chat.use_llm}")
print(f"  - Will use: {'LLM' if chat.use_llm else 'FALLBACK TEMPLATES'}")

# Test actual chat
result = chat.chat("What is data quality?")
print("\nSample response:")
print(f"  {result['response'][:150]}...")

# Check if it's a template response
is_template = (
    "encompasses several key aspects" in result["response"].lower()
    or "based on the documentation" in result["response"].lower()
)
print(f"\n⚠️  Using templates: {is_template}")

print("\n" + "=" * 70)
print("🔍 ANÁLISE DO PROBLEMA")
print("=" * 70)

if not chat.use_llm:
    print("\n❌ PROBLEMA IDENTIFICADO:")
    print("   O sistema está usando FALLBACK TEMPLATES em vez da LLM")
    print("\n🔍 Causas possíveis:")
    print("   1. Variáveis de ambiente não configuradas no Render")
    print("   2. Pacote google-generativeai não instalado")
    print("   3. API key inválida ou expirada")
    print("   4. Provider configurado incorretamente")
    print("\n✅ SOLUÇÃO:")
    print("   Verificar no Render Dashboard:")
    print("   - LLM_PROVIDER está definido?")
    print("   - GEMINI_API_KEY está definida?")
    print("   - GEMINI_MODEL está definido?")
    print("\n   Verificar nos logs do Render:")
    print("   - Procurar por '⚠️  Could not initialize LLM client'")
    print("   - Ver qual erro específico aparece")
else:
    print("\n✅ LLM está configurada corretamente!")
