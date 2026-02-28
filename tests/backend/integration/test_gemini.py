"""Integration smoke-tests for the Gemini provider.

These checks hit the live Gemini API and therefore are skipped by default.
Set RUN_GEMINI_TESTS=true (and GEMINI_API_KEY) to exercise them locally.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

RUN_GEMINI_TESTS = os.getenv("RUN_GEMINI_TESTS", "false").lower() == "true"

pytestmark = pytest.mark.skipif(
    not RUN_GEMINI_TESTS,
    reason="Gemini integration tests disabled. Set RUN_GEMINI_TESTS=true to run them.",
)


def _require_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.fail(
            "GEMINI_API_KEY não configurada. Defina GEMINI_API_KEY e RUN_GEMINI_TESTS=true para executar este teste.",
            pytrace=False,
        )
    return api_key


def _print_step(title: str) -> None:
    print(f"\n{title}")


def test_gemini_full_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validate Gemini client wiring end-to-end when explicitly enabled."""

    print("=" * 70)
    print("🧪 TESTE DE INTEGRAÇÃO GEMINI API")
    print("=" * 70)

    api_key = _require_api_key()

    _print_step("1️⃣ Verificando API key...")
    print(f"   ✅ API key configurada: {api_key[:20]}...")

    from llm_client import GeminiClient, create_llm_client  # type: ignore  # noqa: E402

    _print_step("2️⃣ Criando cliente Gemini...")
    client = GeminiClient(
        api_key=api_key, model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    )
    print(f"   ✅ Cliente criado: {client.model_name}")

    _print_step("3️⃣ Testando geração de texto...")
    response = client.generate(
        messages=[
            {"role": "user", "content": "What is data quality? Answer in 2 sentences."}
        ],
        system="You are a helpful data engineering assistant.",
        max_tokens=100,
        temperature=0.7,
    )
    assert (
        isinstance(response, str) and response.strip()
    ), "Resposta vazia da API Gemini"
    print(f"   ✅ Resposta gerada com sucesso: {response[:200]}...")

    _print_step("4️⃣ Testando função factory...")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", api_key)
    llm = create_llm_client()
    factory_response = llm.generate(
        messages=[{"role": "user", "content": "Say hello in one word"}], max_tokens=10
    )
    assert (
        isinstance(factory_response, str) and factory_response.strip()
    ), "Factory retornou resposta vazia"
    print(f"   ✅ Teste rápido: {factory_response}")

    _print_step("5️⃣ Testando integração com RAG...")
    from rag.config_simple import RAGConfig  # type: ignore  # noqa: E402
    from rag.simple_rag import SimpleRAG  # type: ignore  # noqa: E402
    from rag.simple_chat import SimpleChatEngine  # type: ignore  # noqa: E402

    config = RAGConfig.from_env()
    rag = SimpleRAG(config)
    chat = SimpleChatEngine(rag)

    if chat.use_llm:
        result: Dict[str, Any] = chat.chat("What is PySpark?")
        assert result.get("response"), "Chat não retornou resposta"
        print("   ✅ RAG configurado com Gemini")
        print(
            f"      Provider: gemini | Modelo: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}"
        )
        print(f"   📝 Resposta do chat: {result['response'][:200]}...")
        print(f"   Citações: {len(result.get('citations', []))}")
    else:
        pytest.fail("RAG não está configurado para usar Gemini")

    print("\n" + "=" * 70)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)
