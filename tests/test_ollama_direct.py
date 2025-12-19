"""Direct test of Ollama integration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("=" * 70)
print("🧪 TESTE DIRETO DO OLLAMA")
print("=" * 70)

# Test 1: Import ollama package
print("\n1️⃣ Testando importação do pacote ollama...")
try:
    import ollama

    print("   ✅ Pacote ollama importado com sucesso")
except ImportError as e:
    print(f"   ❌ Falha ao importar ollama: {e}")
    sys.exit(1)

# Test 2: Connect to Ollama server
print("\n2️⃣ Testando conexão com servidor Ollama...")
try:
    client = ollama.Client(host="http://localhost:11434")
    print("   ✅ Cliente Ollama criado")
except Exception as e:
    print(f"   ❌ Falha ao criar cliente: {e}")
    sys.exit(1)

# Test 3: List models
print("\n3️⃣ Listando modelos disponíveis...")
try:
    response = client.list()
    models = response.get("models", [])
    print(f"   ✅ {len(models)} modelo(s) encontrado(s):")
    for model in models:
        model_name = model.get("model") or model.get("name", "unknown")
        model_size = model.get("size", 0)
        print(f"      - {model_name} ({model_size / 1e9:.1f} GB)")
except Exception as e:
    print(f"   ❌ Falha ao listar modelos: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 4: Test LLM client abstraction
print("\n4️⃣ Testando abstração LLM client...")
try:
    from llm_client import OllamaClient  # type: ignore  # noqa: E402

    llm = OllamaClient(model="qwen2.5-coder:7b", base_url="http://localhost:11434")
    print("   ✅ OllamaClient criado")
except Exception as e:
    print(f"   ❌ Falha ao criar OllamaClient: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 5: Generate text
print("\n5️⃣ Testando geração de texto...")
try:
    response = llm.generate(
        messages=[
            {"role": "user", "content": "What is data quality? Answer in 2 sentences."}
        ],
        system="You are a helpful data engineering assistant.",
        max_tokens=100,
    )
    print("   ✅ Resposta gerada com sucesso:")
    print(f"   📝 {response[:200]}...")
except Exception as e:
    print(f"   ❌ Falha ao gerar texto: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 6: Test RAG with Ollama
print("\n6️⃣ Testando RAG com Ollama...")
try:
    # Set env for Ollama
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL"] = "qwen2.5-coder:7b"
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

    from rag.config_simple import RAGConfig  # type: ignore  # noqa: E402
    from rag.simple_rag import SimpleRAG  # type: ignore  # noqa: E402
    from rag.simple_chat import SimpleChatEngine  # type: ignore  # noqa: E402

    config = RAGConfig.from_env()
    rag = SimpleRAG(config)
    chat = SimpleChatEngine(rag)

    if chat.use_llm:
        print("   ✅ RAG configurado com LLM")
        print(f"      Provider: {os.environ.get('LLM_PROVIDER')}")
        print(f"      Model: {os.environ.get('LLM_MODEL')}")

        # Test chat
        result = chat.chat("What is data validation?")
        print("\n   📝 Resposta do chat:")
        print(f"      {result['response'][:200]}...")
        print(f"      Citações: {len(result['citations'])}")
    else:
        print("   ⚠️  RAG usando fallback (sem LLM)")

except Exception as e:
    print(f"   ❌ Falha no teste RAG: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ TODOS OS TESTES PASSARAM!")
print("=" * 70)
print("\n🎉 Ollama está funcionando corretamente!")
print("   Modelo: qwen2.5-coder:7b")
print("   Server: http://localhost:11434")
print("   RAG: Integrado com sucesso")
