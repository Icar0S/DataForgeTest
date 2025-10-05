#!/usr/bin/env python3
"""
Teste final do sistema RAG melhorado.
"""

import requests
import json


def test_improved_rag():
    """Testa o sistema RAG melhorado."""
    print("=== TESTE SISTEMA RAG MELHORADO ===\n")

    # Teste 1: Nova rota de search
    print("1. Testando nova rota /search:")
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/rag/search",
            json={"query": "data quality", "max_results": 3},
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Search funcionando: {len(data['results'])} resultados")
            for i, result in enumerate(data["results"][:2]):
                print(f"   [{i+1}] {result['text'][:80]}...")
        else:
            print(f"   ❌ Search falhou: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Erro na busca: {e}")

    print()

    # Teste 2: Chat melhorado
    test_questions = [
        "What is data quality?",
        "How do I validate my data?",
        "What are common data quality issues?",
        "Tell me about null values in datasets",
    ]

    print("2. Testando chat melhorado:")
    for question in test_questions:
        print(f"\nPergunta: '{question}'")
        try:
            response = requests.post(
                "http://127.0.0.1:5000/api/rag/chat", json={"message": question}
            )

            if response.status_code == 200:
                data = response.json()
                response_text = data["response"]
                citations = data["citations"]

                print(f"   ✓ Resposta ({len(response_text)} chars):")
                # Imprimir primeiras linhas da resposta
                lines = response_text.split("\n")
                for line in lines[:4]:
                    if line.strip():
                        print(f"     {line[:100]}{'...' if len(line) > 100 else ''}")

                print(f"   ✓ Citações: {len(citations)}")

            else:
                print(f"   ❌ Chat falhou: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro no chat: {e}")

    print("\n=== TESTE CONCLUÍDO ===")


if __name__ == "__main__":
    test_improved_rag()
