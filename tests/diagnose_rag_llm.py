"""Diagnóstico detalhado do RAG + LLM."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Configure Gemini
os.environ["LLM_PROVIDER"] = "gemini"
# API key must be set via environment variable
if "GEMINI_API_KEY" not in os.environ:
    raise ValueError("GEMINI_API_KEY environment variable is required")
os.environ["GEMINI_MODEL"] = "gemini-2.5-flash-lite"

from rag.config_simple import RAGConfig  # type: ignore  # noqa: E402
from rag.simple_rag import SimpleRAG  # type: ignore  # noqa: E402
from rag.simple_chat import SimpleChatEngine  # type: ignore  # noqa: E402

print("=" * 80)
print("🔍 DIAGNÓSTICO DETALHADO: RAG + LLM")
print("=" * 80)

# Initialize
config = RAGConfig.from_env()
rag = SimpleRAG(config)
chat = SimpleChatEngine(rag)

print("\n📊 Status do Sistema:")
print(f"  Documentos: {len(rag.documents)}")
print(f"  LLM Ativo: {chat.use_llm}")
print(f"  Provider: {os.getenv('LLM_PROVIDER')}")
print(f"  Model: {os.getenv('GEMINI_MODEL')}")

# Test multiple questions
questions = [
    "What is PySpark?",
    "How do I validate data quality?",
    "What are the best practices for Spark performance?",
    "Explain data validation strategies",
    "What is Apache Spark used for?",
]

for i, question in enumerate(questions, 1):
    print("\n" + "=" * 80)
    print(f"📝 TESTE {i}/5: {question}")
    print("=" * 80)

    # First, check RAG search results
    search_results = rag.search(question)
    print(f"\n🔍 RAG Search encontrou {len(search_results)} resultados:")
    for j, result in enumerate(search_results[:2], 1):  # Show first 2
        print(f"\n  Resultado {j}:")
        print(f"    Relevância: {result.get('score', 0):.3f}")
        print(f"    Fonte: {result['metadata'].get('source', 'Unknown')}")
        print("    Texto (primeiros 200 chars):")
        print(f"    {result['text'][:200]}...")

    # Now get chat response
    result = chat.chat(question)

    print(f"\n💬 Resposta da LLM ({len(result['response'])} chars):")
    print(f"  {result['response']}")

    print(f"\n📎 Citações: {len(result['citations'])}")

    # Analyze response quality
    response_lower = result["response"].lower()
    issues = []

    if len(result["response"]) < 100:
        issues.append("Resposta muito curta")
    if "does not contain" in response_lower or "no information" in response_lower:
        issues.append("LLM diz que não tem informação")
    if "based on the documentation" in response_lower:
        issues.append("Parece template de fallback")
    if "[1]" not in result["response"] and "[2]" not in result["response"]:
        issues.append("Sem citações no texto")

    if issues:
        print("\n⚠️  Problemas detectados:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("\n✅ Resposta parece boa!")

    # Stop after first problematic one for analysis
    if issues and i == 1:
        print("\n" + "=" * 80)
        print("🔎 ANÁLISE DETALHADA DO PROBLEMA")
        print("=" * 80)

        # Check what context was sent to LLM
        print("\n1. Verificando contexto RAG:")
        print(f"   - {len(search_results)} resultados encontrados")
        print(f"   - Score do melhor: {search_results[0].get('score', 0):.3f}")

        # Check citations
        print("\n2. Verificando citações:")
        for idx, citation in enumerate(result["citations"][:2], 1):
            print(f"   Citação {idx}:")
            print(f"     - Texto: {citation['text'][:100]}...")
            print(f"     - Metadata: {citation.get('metadata', {})}")

        # Try direct LLM call with explicit context
        print("\n3. Testando LLM diretamente com contexto:")
        context_text = search_results[0]["text"][:500]

        try:
            from llm_client import get_default_llm_client  # type: ignore  # noqa: E402

            llm = get_default_llm_client()

            direct_response = llm.generate(
                messages=[
                    {
                        "role": "user",
                        "content": f"""Based on this context, answer the question.

Context:
{context_text}

Question: {question}

Answer concisely using the context above.""",
                    }
                ],
                max_tokens=200,
            )

            print(f"   Resposta direta: {direct_response[:200]}...")

            if (
                "does not" in direct_response.lower()
                or "no information" in direct_response.lower()
            ):
                print(
                    "\n   ❌ LLM ainda diz que não tem info mesmo com contexto direto!"
                )
                print("   Possível problema no formato do contexto enviado ao Gemini")
            else:
                print("\n   ✅ LLM responde bem quando contexto é passado diretamente")
                print(
                    "   Problema pode estar em como SimpleChatEngine monta o contexto"
                )
        except Exception as e:
            print(f"   ❌ Erro ao testar LLM diretamente: {e}")

print("\n" + "=" * 80)
print("📊 RESUMO DO DIAGNÓSTICO")
print("=" * 80)
print("\nSe as respostas estão vagas/ruins mas RAG encontra documentos relevantes,")
print("o problema pode estar em:")
print("  1. Formato do contexto enviado ao Gemini")
print("  2. Sistema prompt não está claro o suficiente")
print("  3. Gemini interpretando mal o formato das citações")
print("  4. Temperatura muito alta/baixa")
