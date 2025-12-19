"""Test Gemini API integration."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("=" * 70)
print("🧪 TESTE DE INTEGRAÇÃO GEMINI API")
print("=" * 70)

# Test 1: Check if API key is set
print("\n1️⃣ Verificando API key...")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("   ⚠️  GEMINI_API_KEY não configurada")
    print("   Configure com: set GEMINI_API_KEY=your-key-here")
    print("   Obtenha sua chave em: https://aistudio.google.com/app/apikey")
    sys.exit(1)
else:
    print(f"   ✅ API key configurada: {api_key[:20]}...")

# Test 2: Import and create client
print("\n2️⃣ Criando cliente Gemini...")
try:
    from llm_client import GeminiClient  # type: ignore  # noqa: E402

    client = GeminiClient(
        api_key=api_key, model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    )
    print(f"   ✅ Cliente criado: {client.model_name}")
except ImportError as e:
    print(f"   ❌ Erro de importação: {e}")
    print("   Instale com: pip install google-generativeai")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Erro ao criar cliente: {e}")
    sys.exit(1)

# Test 3: Generate simple text
print("\n3️⃣ Testando geração de texto...")
try:
    response = client.generate(
        messages=[
            {"role": "user", "content": "What is data quality? Answer in 2 sentences."}
        ],
        system="You are a helpful data engineering assistant.",
        max_tokens=100,
        temperature=0.7,
    )
    print("   ✅ Resposta gerada com sucesso:")
    print(f"   📝 {response[:200]}...")
except Exception as e:
    print(f"   ❌ Erro ao gerar texto: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 4: Test factory function
print("\n4️⃣ Testando função factory...")
try:
    os.environ["LLM_PROVIDER"] = "gemini"
    os.environ["GEMINI_API_KEY"] = api_key

    from llm_client import create_llm_client  # type: ignore  # noqa: E402

    llm = create_llm_client()
    print("   ✅ Cliente criado via factory")

    response = llm.generate(
        messages=[{"role": "user", "content": "Say hello in one word"}], max_tokens=10
    )
    print(f"   ✅ Teste rápido: {response}")
except Exception as e:
    print(f"   ❌ Erro no factory: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 5: Test RAG integration
print("\n5️⃣ Testando integração com RAG...")
try:
    from rag.config_simple import RAGConfig  # type: ignore  # noqa: E402
    from rag.simple_rag import SimpleRAG  # type: ignore  # noqa: E402
    from rag.simple_chat import SimpleChatEngine  # type: ignore  # noqa: E402

    config = RAGConfig.from_env()
    rag = SimpleRAG(config)
    chat = SimpleChatEngine(rag)

    if chat.use_llm:
        print("   ✅ RAG configurado com Gemini")
        print("      Provider: gemini")
        print(f"      Model: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")

        # Test chat
        result = chat.chat("What is PySpark?")
        print("\n   📝 Resposta do chat:")
        print(f"      {result['response'][:200]}...")
        print(f"      Citações: {len(result['citations'])}")
    else:
        print("   ⚠️  RAG não configurado com LLM")
except Exception as e:
    print(f"   ❌ Erro na integração RAG: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ TODOS OS TESTES PASSARAM!")
print("=" * 70)
print("\n🎉 Gemini está funcionando corretamente!")
print(f"   Modelo: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")
print("   Provider: gemini")
print("   RAG: Integrado com sucesso")
print("\n📋 CONFIGURAÇÃO PARA RENDER:")
print("   LLM_PROVIDER=gemini")
print(f"   GEMINI_API_KEY={api_key[:20]}...")
print(f"   GEMINI_MODEL={os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")
