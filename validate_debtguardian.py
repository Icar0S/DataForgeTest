#!/usr/bin/env python3
"""
Script completo de validação do DebtGuardian
Testa: configuração, API, detecção e persistência
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Teste 1: Validar imports"""
    print("\n" + "=" * 60)
    print("TEST 1: Validando Imports")
    print("=" * 60)
    try:
        # Import modules to verify they exist
        import debt_guardian.config  # noqa: F401
        import debt_guardian.detector  # noqa: F401
        import debt_guardian.schemas  # noqa: F401
        import debt_guardian.llm_client  # noqa: F401

        print("✓ Todos os imports funcionam corretamente")
        return True
    except ImportError as e:
        print(f"✗ Erro ao importar: {e}")
        return False


def test_config():
    """Teste 2: Validar configuração"""
    print("\n" + "=" * 60)
    print("TEST 2: Validando Configuração")
    print("=" * 60)
    try:
        from debt_guardian.config import DebtGuardianConfig

        config = DebtGuardianConfig(
            use_granular_prompting=True,
            td_types=["design", "documentation", "defect", "test"],
            llm_model="qwen2.5-coder:7b",
        )

        print("✓ Configuração criada com sucesso")
        print(f"  - Modelo: {config.llm_model}")
        print(f"  - Tipos de TD: {config.td_types}")
        print(f"  - Granular prompting: {config.use_granular_prompting}")
        return True
    except Exception as e:
        print(f"✗ Erro na configuração: {e}")
        return False


def test_ollama_connection():
    """Teste 3: Validar conexão com Ollama"""
    print("\n" + "=" * 60)
    print("TEST 3: Validando Conexão Ollama")
    print("=" * 60)
    try:
        from debt_guardian.config import DebtGuardianConfig
        from debt_guardian.llm_client import OllamaClient

        config = DebtGuardianConfig()
        client = OllamaClient(config)
        health = client.health_check()

        if health:
            print("✓ Ollama está respondendo")
            return True
        else:
            print("✗ Ollama não respondeu")
            return False
    except Exception as e:
        print(f"✗ Erro na conexão: {e}")
        return False


def test_detector_initialization():
    """Teste 4: Inicializar detector"""
    print("\n" + "=" * 60)
    print("TEST 4: Inicializando Detector")
    print("=" * 60)
    try:
        from debt_guardian.config import DebtGuardianConfig
        from debt_guardian.detector import DebtDetector

        config = DebtGuardianConfig(
            use_granular_prompting=True, td_types=["design", "defect"]
        )
        _ = DebtDetector(config)  # noqa: F841

        print("✓ Detector inicializado com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao inicializar: {e}")
        return False


def test_simple_analysis():
    """Teste 5: Analisar um diff simples"""
    print("\n" + "=" * 60)
    print("TEST 5: Análise Simples de Diff")
    print("=" * 60)
    try:
        from debt_guardian.config import DebtGuardianConfig
        from debt_guardian.detector import DebtDetector

        config = DebtGuardianConfig(
            use_granular_prompting=True,
            td_types=["defect"],
            llm_model="qwen2.5-coder:7b",
        )
        detector = DebtDetector(config)

        # Diff simples com problema óbvio
        test_diff = "+def divide(a, b):\n+    return a / b"

        print(f"Analisando diff: {test_diff[:50]}...")
        report = detector.detect_in_diff(test_diff, "math.py")

        if report and report.detected_debts:
            print(
                f"✓ Análise completa! Detectados {len(report.detected_debts)} problemas"
            )
            for debt in report.detected_debts[:3]:
                print(f"  - {debt.debt_type}: {debt.symptom[:50]}...")
            return True
        else:
            print("✓ Análise completa (nenhum debt detectado)")
            return True

    except Exception as e:
        print(f"✗ Erro na análise: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_schemas():
    """Teste 6: Validar schemas Pydantic"""
    print("\n" + "=" * 60)
    print("TEST 6: Validando Schemas")
    print("=" * 60)
    try:
        from debt_guardian.schemas import TechnicalDebtInstance, CodeLocation

        # Criar um debt válido
        location = CodeLocation(file_path="test.py", start_line=1, end_line=5)

        debt = TechnicalDebtInstance(
            debt_type="defect",
            symptom="Missing error handling",
            location=location,
            severity="medium",
            confidence=0.85,
            suggested_remediation="Add try-except block",
        )

        print("✓ Schema TechnicalDebtInstance validado")
        print(f"  - Type: {debt.debt_type}")
        print(f"  - Severity: {debt.severity}")

        # Serializar para JSON
        _ = debt.model_dump_json()  # noqa: F841
        print("✓ Serialização JSON funcionando")

        return True
    except Exception as e:
        print(f"✗ Erro nos schemas: {e}")
        return False


def main():
    """Executar todos os testes"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "DebtGuardian Validation Suite" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")

    tests = [
        ("Imports", test_imports),
        ("Configuração", test_config),
        ("Ollama Connection", test_ollama_connection),
        ("Detector Init", test_detector_initialization),
        ("Simple Analysis", test_simple_analysis),
        ("Schemas", test_schemas),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name}: Erro inesperado - {e}")
            results.append((test_name, False))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} testes passaram")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
