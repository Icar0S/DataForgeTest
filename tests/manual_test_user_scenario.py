#!/usr/bin/env python3
"""
Manual test to demonstrate the fixes for the accuracy comparison tool.
This reproduces the user's scenario with multiple key columns and shows
that original key values are preserved in the differences report.
"""

import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.accuracy.processor import compare_and_correct


def test_user_scenario():
    """
    Test case reproducing the user's scenario:
    - Dataset with 47 columns (simplified to 10 for this demo)
    - 3 key columns: ano, mes, uf
    - Multiple value columns including imposto
    - Shows that original key values are preserved (e.g., 'SP' not 'sp')
    """
    print("=" * 80)
    print("Testing User Scenario: Multiple Key Columns with Original Values")
    print("=" * 80)

    # Create GOLD dataset similar to user's data
    gold_df = pd.DataFrame(
        {
            "Ano": [2023, 2023, 2023, 2023, 2024, 2024],
            "Mês": [1, 1, 2, 2, 1, 1],
            "UF": ["SP", "RJ", "MG", "SP", "RJ", "SP"],
            "Produto": ["A", "B", "C", "D", "E", "F"],
            "Quantidade": [100, 200, 150, 300, 250, 180],
            "Preço Unitário": [10.50, 15.00, 12.75, 20.00, 18.50, 14.25],
            "Imposto Pago": [1050.00, 3000.00, 1912.50, 6000.00, 4625.00, 2565.00],
            "Total": [2100.00, 6000.00, 3825.00, 12000.00, 9250.00, 5130.00],
        }
    )

    # Create TARGET dataset with some differences
    target_df = pd.DataFrame(
        {
            "Ano": [2023, 2023, 2023, 2023, 2024, 2024],
            "Mês": [1, 1, 2, 2, 1, 1],
            "UF": ["SP", "RJ", "MG", "SP", "RJ", "SP"],
            "Produto": ["A", "B", "C", "D", "E", "F"],
            "Quantidade": [100, 200, 150, 300, 250, 180],
            "Preço Unitário": [10.50, 15.00, 12.75, 20.00, 18.50, 14.25],
            "Imposto Pago": [
                1050.00,
                3500.00,
                1912.50,
                6500.00,
                4625.00,
                2565.00,
            ],  # RJ and SP diferentes
            "Total": [2100.00, 6000.00, 3825.00, 12000.00, 9250.00, 5130.00],
        }
    )

    print("\n1. GOLD Dataset:")
    print(gold_df[["Ano", "Mês", "UF", "Imposto Pago"]].to_string(index=False))

    print("\n2. TARGET Dataset (with differences):")
    print(target_df[["Ano", "Mês", "UF", "Imposto Pago"]].to_string(index=False))

    print("\n3. Running comparison with key columns: Ano, Mês, UF")
    print("   Value column to check: Imposto Pago")

    # Run comparison
    corrected_df, summary, differences = compare_and_correct(
        gold_df,
        target_df,
        key_columns=["Ano", "Mês", "UF"],
        value_columns=["Imposto Pago"],
        options={
            "normalizeKeys": True,
            "lowercase": True,
            "stripAccents": True,
            "coerceNumeric": True,
            "decimalPlaces": 2,
        },
    )

    print("\n4. Summary:")
    print(f"   Total rows in GOLD: {summary['rows_gold']}")
    print(f"   Total rows in TARGET: {summary['rows_target']}")
    print(f"   Common keys: {summary['common_keys']}")
    print(f"   Mismatches found: {summary['mismatches_total']}")
    print(f"   Accuracy: {summary['accuracy'] * 100:.2f}%")

    print("\n5. Differences Found:")
    print("   " + "-" * 76)
    print(
        "   {:<8} {:<5} {:<4} | {:<15} | {:<12} | {:<12} | {:<12}".format(
            "Ano", "Mês", "UF", "Column", "GOLD", "TARGET", "CORRECTED"
        )
    )
    print("   " + "-" * 76)

    for diff in differences:
        keys = diff["keys"]
        print(
            "   {:<8} {:<5} {:<4} | {:<15} | {:<12.2f} | {:<12.2f} | {:<12.2f}".format(
                keys.get("ano", "N/A"),
                keys.get("mes", "N/A"),
                keys.get("uf", "N/A"),
                diff["column"],
                diff["gold"] or 0,
                diff["target"] or 0,
                diff["corrected"] or 0,
            )
        )

    print("\n6. Verification: Original Key Values Preserved")
    print("   " + "-" * 76)
    for i, diff in enumerate(differences, 1):
        keys = diff["keys"]
        print(f"   Difference {i}:")
        print(f"      - Ano type: {type(keys['ano']).__name__} = {keys['ano']}")
        print(f"      - Mês type: {type(keys['mes']).__name__} = {keys['mes']}")
        print(
            f"      - UF type: {type(keys['uf']).__name__} = '{keys['uf']}' (NOT normalized to lowercase)"
        )

        # Verify UF is uppercase (original value)
        assert keys["uf"] in [
            "SP",
            "RJ",
            "MG",
        ], f"UF should be original uppercase, got: {keys['uf']}"
        # Verify ano and mes are integers
        assert isinstance(
            keys["ano"], int
        ), f"Ano should be int, got: {type(keys['ano'])}"
        assert isinstance(
            keys["mes"], int
        ), f"Mês should be int, got: {type(keys['mes'])}"
        print(f"      ✓ All key values are original (not normalized)")

    print("\n7. Corrected Dataset Sample:")
    print(corrected_df[["ano", "mes", "uf", "imposto_pago"]].to_string(index=False))

    print("\n" + "=" * 80)
    print("✅ TEST PASSED: Original key values are preserved correctly!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    try:
        test_user_scenario()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
