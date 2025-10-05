#!/usr/bin/env python3
"""
Script para testar e diagnosticar o sistema RAG.
"""

import requests
import time

# Configuração da API
API_BASE = "http://127.0.0.1:5000/api/rag"


def test_rag_debug():
    """Testa o endpoint de debug."""
    print("=== TESTE DEBUG RAG ===\n")

    try:
        response = requests.get(f"{API_BASE}/debug")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Documentos: {data['documents_count']}")
            print(f"✓ Chunks: {data['chunks_count']}")
            print("\nDocumentos carregados:")
            for doc in data["documents"]:
                print(f"  - {doc['filename']} ({doc['content_length']} chars)")
            return True
        else:
            print(f"❌ Erro: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False


def test_rag_search():
    """Testa busca direta no RAG."""
    print("\n=== TESTE BUSCA RAG ===\n")

    test_queries = [
        "data quality",
        "what is data validation?",
        "how to check data quality?",
        "null values in data",
    ]

    for query in test_queries:
        print(f"Consultando: '{query}'")
        try:
            response = requests.post(
                f"{API_BASE}/search", json={"query": query, "max_results": 3}
            )

            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"  ✓ {len(results.get('results', []))} resultados encontrados")

                for i, result in enumerate(results.get("results", [])[:2]):
                    print(f"    [{i+1}] {result['text'][:100]}...")
            else:
                print(f"  ❌ Erro: {response.text}")

        except Exception as e:
            print(f"  ❌ Erro: {e}")
        print()


def test_rag_chat():
    """Testa chat com RAG."""
    print("=== TESTE CHAT RAG ===\n")

    test_messages = [
        "What is data quality?",
        "How can I validate my data?",
        "What are common data quality issues?",
        "Tell me about null values",
    ]

    for message in test_messages:
        print(f"Pergunta: '{message}'")
        try:
            response = requests.post(f"{API_BASE}/chat", json={"message": message})

            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Resposta ({len(data['response'])} chars):")
                print(f"    {data['response'][:200]}...")
                print(f"  ✓ Citações: {len(data['citations'])}")

                for i, citation in enumerate(data["citations"][:2]):
                    print(f"    [{citation['id']}] {citation['text'][:80]}...")
            else:
                print(f"  ❌ Erro: {response.text}")

        except Exception as e:
            print(f"  ❌ Erro: {e}")
        print()


def test_direct_rag_access():
    """Testa acesso direto ao sistema RAG interno."""
    print("=== TESTE ACESSO DIRETO ===\n")

    try:
        # Importar e testar diretamente
        import sys
        import os

        # Add the parent directory to path to access src modules
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        src_dir = os.path.join(parent_dir, "src")
        sys.path.insert(0, src_dir)

        from config import RAGConfig
        from simple_rag import SimpleRAG
        from chat import SimpleChatEngine

        # Inicializar
        config = RAGConfig.from_env()
        rag_system = SimpleRAG(config)
        chat_engine = SimpleChatEngine(rag_system)

        print(
            f"✓ RAG system carregado: {len(rag_system.documents)} docs, {len(rag_system.document_chunks)} chunks"
        )

        # Testar busca
        search_results = rag_system.search("data quality", max_results=3)
        print(f"✓ Busca 'data quality': {len(search_results)} resultados")

        if search_results:
            print(f"  Primeiro resultado: {search_results[0]['text'][:100]}...")

        # Testar chat
        chat_result = chat_engine.chat("What is data quality?")
        print(f"✓ Chat response: {len(chat_result['response'])} chars")
        print(f"  {chat_result['response'][:150]}...")

        return True

    except Exception as e:
        print(f"❌ Erro no teste direto: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Iniciando diagnóstico do sistema RAG...\n")

    # Aguardar um pouco para garantir que a API está pronta
    time.sleep(1)

    # Executar testes
    debug_ok = test_rag_debug()

    if debug_ok:
        test_rag_search()
        test_rag_chat()

    test_direct_rag_access()

    print("\n=== DIAGNÓSTICO CONCLUÍDO ===")
