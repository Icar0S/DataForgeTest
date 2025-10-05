#!/usr/bin/env python3
"""
Script para testar o download de arquivos CSV da API synthetic.
Verifica se o problema de "dataset.htm" foi corrigido.
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuração da API
API_BASE = "http://127.0.0.1:5000/api/synth"


def test_csv_download():
    """
    Testa o processo completo de geração e download de CSV.
    """
    print("=== TESTE DE DOWNLOAD DE CSV ===\n")

    # 1. Testar health check
    print("1. Verificando health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ API está rodando: {response.json()['message']}")
        else:
            print(f"   ❌ API não está respondendo")
            return False
    except Exception as e:
        print(f"   ❌ Erro ao conectar na API: {e}")
        return False

    # 2. Gerar um dataset pequeno
    print("\n2. Gerando dataset de teste...")

    # Schema simples para teste
    test_schema = {
        "columns": [
            {
                "name": "nome",
                "type": "string",
                "description": "Nome completo de pessoa",
            },
            {
                "name": "email",
                "type": "email",
                "description": "Endereço de email válido",
            },
            {
                "name": "idade",
                "type": "integer",
                "description": "Idade entre 18 e 80 anos",
            },
        ]
    }

    generate_request = {
        "schema": test_schema,
        "rows": 10,
        "fileType": "csv",
        "llmMode": "full",
        "locale": "pt_BR",
    }

    try:
        response = requests.post(
            f"{API_BASE}/generate",
            json=generate_request,
            headers={"Content-Type": "application/json"},
        )

        print(f"   Status: {response.status_code}")

        if response.status_code != 200:
            print(f"   ❌ Erro na geração: {response.text}")
            return False

        result = response.json()
        download_url = result["downloadUrl"]
        print(f"   ✓ Dataset gerado: {result['summary']['rows']} linhas")
        print(f"   ✓ URL de download: {download_url}")

    except Exception as e:
        print(f"   ❌ Erro na geração: {e}")
        return False

    # 3. Testar download
    print("\n3. Testando download...")

    try:
        download_response = requests.get(f"http://127.0.0.1:5000{download_url}")

        print(f"   Status: {download_response.status_code}")
        print(
            f"   Content-Type: {download_response.headers.get('Content-Type', 'N/A')}"
        )
        print(
            f"   Content-Disposition: {download_response.headers.get('Content-Disposition', 'N/A')}"
        )
        print(
            f"   Content-Length: {download_response.headers.get('Content-Length', 'N/A')} bytes"
        )

        if download_response.status_code == 200:
            # Verificar se o conteúdo é realmente CSV
            content = download_response.text
            lines = content.strip().split("\n")

            print(f"   ✓ Arquivo baixado com sucesso")
            print(f"   ✓ Linhas no arquivo: {len(lines)}")
            print(f"   ✓ Primeira linha (header): {lines[0] if lines else 'Vazio'}")

            # Verificar se parece com CSV
            if lines and "," in lines[0]:
                print(f"   ✓ Conteúdo parece ser CSV válido")

                # Salvar arquivo de teste para verificação manual
                test_file = Path("test_download.csv")
                test_file.write_text(content, encoding="utf-8")
                print(f"   ✓ Arquivo salvo como {test_file} para verificação manual")

                return True
            else:
                print(f"   ❌ Conteúdo não parece ser CSV")
                print(f"   Primeiras linhas:")
                for i, line in enumerate(lines[:3]):
                    print(f"     {i+1}: {line[:100]}...")
                return False
        else:
            print(f"   ❌ Erro no download: {download_response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Erro no download: {e}")
        return False


def test_download_headers():
    """
    Testa especificamente os cabeçalhos HTTP do download.
    """
    print("\n=== TESTE DETALHADO DE CABEÇALHOS ===\n")

    # Usar uma URL de download existente (se houver) ou gerar uma nova
    print("Gerando URL de download temporária...")

    test_schema = {
        "columns": [
            {"name": "id", "type": "integer", "description": "ID sequencial"},
            {"name": "nome", "type": "string", "description": "Nome de pessoa"},
        ]
    }

    generate_request = {
        "schema": test_schema,
        "rows": 5,
        "fileType": "csv",
        "llmMode": "full",
    }

    try:
        response = requests.post(f"{API_BASE}/generate", json=generate_request)
        if response.status_code == 200:
            download_url = response.json()["downloadUrl"]

            # Fazer requisição HEAD para verificar cabeçalhos
            head_response = requests.head(f"http://127.0.0.1:5000{download_url}")
            print("Cabeçalhos da resposta HEAD:")
            for header, value in head_response.headers.items():
                print(f"  {header}: {value}")

            # Fazer requisição GET para verificar cabeçalhos
            get_response = requests.get(f"http://127.0.0.1:5000{download_url}")
            print("\nCabeçalhos da resposta GET:")
            for header, value in get_response.headers.items():
                print(f"  {header}: {value}")

            # Verificar conteúdo
            print(
                f"\nTipo de conteúdo detectado pelo requests: {get_response.headers.get('content-type')}"
            )
            print(f"Tamanho do conteúdo: {len(get_response.content)} bytes")

            return True
        else:
            print(f"Erro ao gerar dataset: {response.text}")
            return False

    except Exception as e:
        print(f"Erro no teste de cabeçalhos: {e}")
        return False


if __name__ == "__main__":
    print("Iniciando testes de download CSV...\n")

    # Aguardar um pouco para garantir que a API está pronta
    time.sleep(2)

    # Executar testes
    success1 = test_csv_download()
    success2 = test_download_headers()

    print(f"\n=== RESULTADO DOS TESTES ===")
    print(f"Teste de download completo: {'✓ PASSOU' if success1 else '❌ FALHOU'}")
    print(f"Teste de cabeçalhos: {'✓ PASSOU' if success2 else '❌ FALHOU'}")

    if success1 and success2:
        print(
            "\n🎉 Todos os testes passaram! O problema do download deve estar corrigido."
        )
    else:
        print("\n⚠️  Alguns testes falharam. Investigação adicional necessária.")
