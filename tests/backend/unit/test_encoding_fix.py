"""Teste específico para verificar se o problema de codificação foi resolvido."""

import tempfile
import pandas as pd
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from src.accuracy.processor import read_dataset


def test_encoding_detection():
    """Teste para verificar diferentes codificações de arquivo."""

    # Dados de teste com caracteres especiais (português/brasileiro)
    test_data = {
        "Nome": ["João da Silva", "María José", "François Müller", "José Antônio"],
        "Cidade": ["São Paulo", "Brasília", "Belo Horizonte", "Florianópolis"],
        "Valor": [1250.50, 890.75, 2100.00, 1450.25],
    }

    df_original = pd.DataFrame(test_data)

    # Testar diferentes codificações
    encodings_to_test = ["utf-8", "latin1", "iso-8859-1", "cp1252", "windows-1252"]

    success_count = 0

    for encoding in encodings_to_test:
        try:
            # Criar arquivo temporário com codificação específica
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False, encoding=encoding
            ) as f:
                df_original.to_csv(f, index=False)
                temp_path = Path(f.name)

            # Tentar ler o arquivo usando nossa função melhorada
            try:
                df_read = read_dataset(temp_path)
                print(f"✅ Codificação {encoding}: SUCESSO")
                print(f"   Linhas lidas: {len(df_read)}")
                print(f"   Colunas: {list(df_read.columns)}")
                success_count += 1
            except Exception as e:
                print(f"❌ Codificação {encoding}: FALHOU - {str(e)}")

            # Limpar arquivo temporário
            try:
                temp_path.unlink()
            except OSError:
                pass

        except Exception as e:
            print(f"❌ Erro ao criar arquivo com codificação {encoding}: {str(e)}")

    print(
        f"\n📊 Resultado: {success_count}/{len(encodings_to_test)} codificações suportadas"
    )

    # Teste adicional: arquivo com byte problemático (simulando o erro original)
    try:
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            # Criar um CSV com bytes problemáticos que causariam o erro original
            content = (
                b"Nome,Valor\nJo\xeao,100\nMaria,200"  # byte 0xea que causava o erro
            )
            f.write(content)
            temp_path = Path(f.name)

        try:
            df_read = read_dataset(temp_path)
            print("✅ Arquivo com bytes problemáticos: SUCESSO")
            print(f"   Linhas lidas: {len(df_read)}")
        except Exception as e:
            print(f"❌ Arquivo com bytes problemáticos: FALHOU - {str(e)}")

        # Limpar
        try:
            temp_path.unlink()
        except OSError:
            pass

    except Exception as e:
        print(f"❌ Erro no teste de bytes problemáticos: {str(e)}")


if __name__ == "__main__":
    print("🧪 Testando detecção automática de codificação...")
    test_encoding_detection()
    print("\n✨ Teste concluído!")
