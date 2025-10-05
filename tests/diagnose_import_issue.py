#!/usr/bin/env python3
"""
Script para diagnosticar problema intermitente de importação do anthropic.
O erro parece estar relacionado à leitura de entry_points.txt de pacotes.
"""

import sys
import os
import traceback
import importlib.metadata
from pathlib import Path


def diagnose_metadata_issue():
    print("=== DIAGNÓSTICO DO PROBLEMA DE IMPORTAÇÃO ===\n")

    print(f"Python: {sys.version}")
    print(f"Virtual env: {sys.prefix}")
    print(f"Site packages: {sys.path}")
    print()

    # Verificar pacotes relacionados
    problematic_packages = ["pydantic", "anthropic"]

    for package_name in problematic_packages:
        print(f"--- Verificando {package_name} ---")
        try:
            # Tentar obter informações de metadados
            dist = importlib.metadata.distribution(package_name)
            print(f"✓ Distribuição encontrada: {dist.metadata['Name']} v{dist.version}")
            print(f"  Localização: {dist.locate_file('')}")

            # Tentar ler entry_points
            try:
                entry_points = dist.entry_points
                print(f"  Entry points: {len(entry_points)} encontrados")

                # Verificar se entry_points.txt existe e é legível
                metadata_path = dist.locate_file("")
                entry_points_file = metadata_path / "entry_points.txt"
                if entry_points_file.exists():
                    print(f"  entry_points.txt existe: {entry_points_file}")
                    try:
                        content = entry_points_file.read_text(encoding="utf-8")
                        print(f"  Tamanho do arquivo: {len(content)} chars")
                    except Exception as e:
                        print(f"  ❌ Erro ao ler entry_points.txt: {e}")
                else:
                    print(f"  entry_points.txt não encontrado em {metadata_path}")

            except Exception as e:
                print(f"  ❌ Erro ao acessar entry_points: {e}")
                traceback.print_exc()

        except Exception as e:
            print(f"❌ Erro ao obter metadados de {package_name}: {e}")
            traceback.print_exc()
        print()


def test_direct_import():
    print("=== TESTE DE IMPORTAÇÃO DIRETA ===\n")

    # Tentar importar pydantic primeiro
    try:
        print("Importando pydantic...")
        import pydantic

        print(f"✓ Pydantic importado: v{pydantic.__version__}")
    except Exception as e:
        print(f"❌ Erro ao importar pydantic: {e}")
        traceback.print_exc()
        return False

    # Tentar importar anthropic
    try:
        print("Importando anthropic...")
        import anthropic

        print(f"✓ Anthropic importado: v{anthropic.__version__}")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar anthropic: {e}")
        traceback.print_exc()
        return False


def test_multiple_imports():
    print("=== TESTE DE MÚLTIPLAS IMPORTAÇÕES ===\n")

    success_count = 0
    total_attempts = 5

    for i in range(total_attempts):
        print(f"Tentativa {i+1}/{total_attempts}...")
        try:
            # Remover módulos do cache para forçar reimportação
            modules_to_remove = [
                mod
                for mod in sys.modules.keys()
                if mod.startswith(("anthropic", "pydantic"))
            ]
            for mod in modules_to_remove:
                del sys.modules[mod]

            import anthropic

            print(f"  ✓ Sucesso")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Falha: {e}")

    print(f"\nResultado: {success_count}/{total_attempts} importações bem-sucedidas")
    print(f"Taxa de sucesso: {(success_count/total_attempts)*100:.1f}%")

    return success_count > 0


if __name__ == "__main__":
    print("Iniciando diagnóstico...\n")

    # Fase 1: Diagnóstico de metadados
    diagnose_metadata_issue()

    # Fase 2: Teste de importação direta
    can_import = test_direct_import()

    # Fase 3: Teste de múltiplas importações se a direta funcionar
    if can_import:
        test_multiple_imports()

    print("\n=== DIAGNÓSTICO CONCLUÍDO ===")
