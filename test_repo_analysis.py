#!/usr/bin/env python3
"""
Teste do DebtGuardian no repositório atual
Analisa os últimos commits do projeto para detectar débitos técnicos
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def main():
    """Executar análise do repositório atual"""
    from debt_guardian.detector import DebtDetector
    from debt_guardian.config import DebtGuardianConfig

    # Caminho do repositório atual
    repo_path = os.path.dirname(os.path.abspath(__file__))

    print("=" * 80)
    print("DebtGuardian - Análise de Repositório")
    print("=" * 80)
    print(f"\nRepositório: {repo_path}")
    print("Branch: copilot/setup-experimental-llm-framework")
    print("\nConfigurando análise...")

    # Configurar o detector
    config = DebtGuardianConfig(
        repo_path=repo_path,
        use_granular_prompting=True,
        td_types=["design", "defect", "documentation", "test"],
        llm_model="qwen2.5-coder:7b",
    )

    print(f"  - Modelo: {config.llm_model}")
    print(f"  - Tipos de TD: {config.td_types}")
    print(f"  - Granular prompting: {config.use_granular_prompting}")

    detector = DebtDetector(config)

    print("\n" + "=" * 80)
    print("Iniciando análise dos últimos 3 commits...")
    print("=" * 80)
    print("\n⏳ Isso pode levar alguns minutos dependendo do tamanho dos commits...\n")

    try:
        # Analisar os últimos 3 commits
        report = detector.analyze_repository(max_commits=3)

        print("\n" + "=" * 80)
        print("RESULTADO DA ANÁLISE")
        print("=" * 80)

        # Mostrar resumo
        print("\n📊 Resumo:")
        print(f"  - Total de débitos detectados: {report.total_debts}")
        print(f"  - Arquivos analisados: {report.total_files}")
        print(f"  - Commits analisados: {report.summary.get('commits_analyzed', 0)}")

        # Coletar todos os débitos de todos os reports
        all_debts = []
        for individual_report in report.reports:
            all_debts.extend(individual_report.detected_debts)

        if all_debts:
            print(f"\n🔍 Débitos Técnicos Encontrados ({len(all_debts)}):")
            print("-" * 80)

            # Agrupar por tipo
            by_type = {}
            for debt in all_debts:
                debt_type = debt.debt_type
                if debt_type not in by_type:
                    by_type[debt_type] = []
                by_type[debt_type].append(debt)

            # Mostrar por tipo
            for debt_type, debts in by_type.items():
                print(f"\n📌 {debt_type.upper()} ({len(debts)} encontrado(s)):")
                for i, debt in enumerate(debts[:5], 1):  # Mostrar no máximo 5 por tipo
                    print(f"\n  {i}. {debt.symptom[:80]}...")
                    print(
                        f"     📍 Local: {debt.location.file_path}:{debt.location.start_line}"
                    )
                    print(f"     ⚠️  Severidade: {debt.severity}")
                    print(f"     🎯 Confiança: {debt.confidence:.2%}")
                    if debt.suggested_remediation:
                        print(f"     💡 Sugestão: {debt.suggested_remediation[:80]}...")

                if len(debts) > 5:
                    print(f"\n  ... e mais {len(debts) - 5} débitos deste tipo")
        else:
            print("\n✅ Nenhum débito técnico detectado!")

        # Salvar relatório completo
        output_file = "debt_guardian_report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        print(f"\n📄 Relatório completo salvo em: {output_file}")

        print("\n" + "=" * 80)
        print("Análise concluída com sucesso!")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ Erro durante a análise: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
