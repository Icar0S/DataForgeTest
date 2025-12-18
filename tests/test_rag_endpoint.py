"""Test RAG chat endpoint via HTTP."""

import requests
import json


def test_rag_endpoint():
    """Test the RAG chat endpoint."""

    print("=" * 70)
    print("🌐 TESTE DO ENDPOINT RAG VIA HTTP")
    print("=" * 70)

    base_url = "http://localhost:5000"

    # Test health
    print("\n🏥 Testando health check...")
    try:
        response = requests.get(f"{base_url}/api/rag/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"   ✓ Status: {data.get('status')}")
            print(f"   ✓ Documentos: {data.get('documents')}")
            print(f"   ✓ LLM: {data.get('llm')}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        print("\n⚠️  Certifique-se que o backend está rodando:")
        print("   cd src && python api.py")
        return

    # Test debug
    print("\n🔍 Testando debug endpoint...")
    try:
        response = requests.get(f"{base_url}/api/rag/debug", timeout=5)
        if response.ok:
            data = response.json()
            print(f"   ✓ Documentos: {data.get('documents_count')}")
            print(f"   ✓ Chunks: {data.get('chunks_count')}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Test chat (non-streaming)
    print("\n💬 Testando chat endpoint (não-streaming)...")
    try:
        test_message = "What are the best practices for Spark?"
        response = requests.post(
            f"{base_url}/api/rag/chat", json={"message": test_message}, timeout=30
        )

        print(f"   Query: '{test_message}'")
        print(f"   Status: {response.status_code}")

        if response.ok:
            data = response.json()
            print(f"\n   Resposta: {data.get('response')[:200]}...")
            print(f"\n   Citações: {len(data.get('citations', []))}")

            for i, citation in enumerate(data.get("citations", [])[:3]):
                filename = citation.get("metadata", {}).get("filename", "Unknown")
                print(f"   [{i+1}] {filename}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Test streaming endpoint
    print("\n📡 Testando chat-stream endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/rag/chat-stream",
            json={"message": "What is data quality?"},
            stream=True,
            timeout=30,
        )

        print(f"   Status: {response.status_code}")

        if response.ok:
            print("   Streaming chunks:")
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        data_str = decoded[6:]
                        if data_str == "[DONE]":
                            print(f"\n   ✓ Stream concluído ({chunk_count} chunks)")
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            if chunk_data.get("type") == "token":
                                chunk_count += 1
                                if chunk_count <= 5:
                                    print(f"      {chunk_data.get('content')}", end="")
                            elif chunk_data.get("type") == "citations":
                                citations = chunk_data.get("content", {}).get(
                                    "citations", []
                                )
                                print(f"\n   ✓ Citações recebidas: {len(citations)}")
                        except:
                            pass
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    print("\n" + "=" * 70)
    print("✅ Teste de endpoints concluído!")
    print("=" * 70)


if __name__ == "__main__":
    test_rag_endpoint()
