#!/usr/bin/env python3
"""
Script para corrigir todas as chamadas fetch() nos componentes do frontend
para usar getApiUrl() permitindo funcionamento em produção
"""

import re
import os

# Arquivos que precisam ser corrigidos
files_to_fix = [
    "frontend/src/pages/ChecklistPage.js",
    "frontend/src/pages/AdvancedPySparkGenerator.js",
    "frontend/src/pages/DatasetMetrics.js",
    "frontend/src/pages/GenerateDataset.js",
    "frontend/src/pages/TestDatasetGold.js",
    "frontend/src/hooks/useDataAccuracy.js",
]


def fix_file(filepath):
    """Corrige um arquivo específico"""
    print(f"\n📝 Processando: {filepath}")

    if not os.path.exists(filepath):
        print(f"   ❌ Arquivo não encontrado!")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    changes = 0

    # 1. Adicionar import do getApiUrl se não existir
    if "getApiUrl" not in content:
        # Encontrar a última linha de import
        import_lines = []
        for i, line in enumerate(content.split("\n")):
            if line.strip().startswith("import "):
                import_lines.append(i)

        if import_lines:
            lines = content.split("\n")
            # Adicionar após o último import
            last_import_line = max(import_lines)
            lines.insert(
                last_import_line + 1, "import { getApiUrl } from '../config/api';"
            )
            content = "\n".join(lines)
            changes += 1
            print(f"   ✅ Import do getApiUrl adicionado")

    # 2. Substituir fetch('/api/...') por fetch(getApiUrl('/api/...'))
    # Padrão 1: com aspas simples
    pattern1 = r"fetch\('(/api/[^']+)'\)"
    matches1 = re.findall(pattern1, content)

    # Padrão 2: com template strings
    pattern2 = r"fetch\(`(/api/[^`]+)`\)"
    matches2 = re.findall(pattern2, content)

    total_matches = matches1 + matches2

    if total_matches:
        print(f"   🔍 Encontradas {len(total_matches)} chamadas fetch para corrigir:")
        for match in total_matches:
            print(f"      - {match}")

        content = re.sub(pattern1, r"fetch(getApiUrl('\1'))", content)
        content = re.sub(pattern2, r"fetch(getApiUrl(`\1`))", content)
        changes += len(total_matches)  # 3. Salvar se houve mudanças
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ✅ Arquivo atualizado com {changes} mudanças!")
        return True
    else:
        print(f"   ℹ️  Nenhuma mudança necessária")
        return False


def main():
    """Processa todos os arquivos"""
    print("=" * 70)
    print("  CORREÇÃO DE CHAMADAS FETCH PARA PRODUÇÃO")
    print("=" * 70)

    total_fixed = 0

    for filepath in files_to_fix:
        if fix_file(filepath):
            total_fixed += 1

    print("\n" + "=" * 70)
    print(f"  RESUMO: {total_fixed}/{len(files_to_fix)} arquivos corrigidos")
    print("=" * 70)

    if total_fixed > 0:
        print("\n✅ Correções aplicadas com sucesso!")
        print("\n📋 Próximos passos:")
        print("   1. Teste localmente: cd frontend && npm start")
        print("   2. Build para produção: npm run build")
        print("   3. Deploy: vercel --prod")
    else:
        print("\nℹ️  Nenhum arquivo precisou de correção")


if __name__ == "__main__":
    main()
