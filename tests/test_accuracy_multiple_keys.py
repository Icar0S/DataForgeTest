"""Test for accuracy comparison with multiple key columns.

This test validates that:
1. Comparison works correctly with multiple key columns
2. Original key values are preserved in difference reports (not normalized values)
3. Comparison handles special characters, accents, and mixed case properly
"""

import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.accuracy.processor import compare_and_correct


class TestMultipleKeyColumns:
    """Test comparison with multiple key columns."""

    def test_original_key_values_preserved(self):
        """Test that original key values are shown in differences, not normalized ones."""
        # Create GOLD dataset with mixed case and accents
        gold_df = pd.DataFrame(
            {
                "Ano": [2023, 2023, 2024],
                "Mês": [1, 2, 1],
                "UF": ["SP", "RJ", "MG"],
                "Imposto Pago": [100.0, 200.0, 150.0],
            }
        )

        # Create TARGET dataset with one difference
        target_df = pd.DataFrame(
            {
                "Ano": [2023, 2023, 2024],
                "Mês": [1, 2, 1],
                "UF": ["SP", "RJ", "MG"],
                "Imposto Pago": [100.0, 250.0, 150.0],  # RJ is different
            }
        )

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

        # Should find 1 difference
        assert len(differences) == 1
        assert summary["mismatches_total"] == 1

        # Check that ORIGINAL key values are preserved (not normalized)
        diff = differences[0]
        assert diff["keys"]["ano"] == 2023, "Ano should be original integer value"
        assert diff["keys"]["mes"] == 2, "Mês should be original integer value"
        assert (
            diff["keys"]["uf"] == "RJ"
        ), "UF should be original 'RJ', not normalized 'rj'"

        # Check the value columns
        assert diff["column"] == "imposto_pago"
        assert diff["gold"] == 200.0
        assert diff["target"] == 250.0
        assert diff["corrected"] == 200.0
        assert diff["delta"] == 50.0

    def test_three_key_columns_with_many_value_columns(self):
        """Test comparison with 3 key columns and multiple value columns (similar to user's case)."""
        # Simulate user's scenario: 47 columns total, 3 keys, 1 value to check
        # Creating a simplified version with fewer columns for testing
        gold_df = pd.DataFrame(
            {
                "ano": [2023, 2023, 2023, 2024],
                "mes": [1, 1, 2, 1],
                "uf": ["SP", "RJ", "SP", "MG"],
                "col1": [1, 2, 3, 4],
                "col2": [10, 20, 30, 40],
                "imposto": [100.0, 200.0, 300.0, 400.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "ano": [2023, 2023, 2023, 2024],
                "mes": [1, 1, 2, 1],
                "uf": ["SP", "RJ", "SP", "MG"],
                "col1": [1, 2, 3, 4],
                "col2": [10, 20, 30, 40],
                "imposto": [100.0, 250.0, 300.0, 450.0],  # Two differences: RJ and MG
            }
        )

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["ano", "mes", "uf"],
            value_columns=["imposto"],
            options={},
        )

        # Should find 2 differences
        assert len(differences) == 2
        assert summary["mismatches_total"] == 2
        assert summary["common_keys"] == 4

        # Verify original key values are preserved for all differences
        for diff in differences:
            # Keys should be original values, not normalized
            assert isinstance(diff["keys"]["ano"], (int, str))
            assert isinstance(diff["keys"]["mes"], (int, str))
            assert diff["keys"]["uf"] in [
                "SP",
                "RJ",
                "MG",
            ], f"UF should be original uppercase value, got: {diff['keys']['uf']}"

        # Check specific differences
        rj_diff = next(d for d in differences if str(d["keys"]["uf"]) == "RJ")
        assert rj_diff["gold"] == 200.0
        assert rj_diff["target"] == 250.0

        mg_diff = next(d for d in differences if str(d["keys"]["uf"]) == "MG")
        assert mg_diff["gold"] == 400.0
        assert mg_diff["target"] == 450.0

    def test_composite_key_with_special_characters(self):
        """Test that composite keys work correctly with special characters and accents."""
        gold_df = pd.DataFrame(
            {
                "Estado": ["São Paulo", "Rio de Janeiro", "Minas Gerais"],
                "Região": ["Sudeste", "Sudeste", "Sudeste"],
                "Valor": [1000.0, 2000.0, 1500.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "Estado": ["São Paulo", "Rio de Janeiro", "Minas Gerais"],
                "Região": ["Sudeste", "Sudeste", "Sudeste"],
                "Valor": [1000.0, 2500.0, 1500.0],  # Rio different
            }
        )

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["Estado", "Região"],
            value_columns=["Valor"],
            options={"normalizeKeys": True, "lowercase": True, "stripAccents": True},
        )

        # Should find 1 difference
        assert len(differences) == 1

        # Original values should be preserved with accents
        diff = differences[0]
        assert (
            diff["keys"]["estado"] == "Rio de Janeiro"
        ), f"Expected 'Rio de Janeiro', got: {diff['keys']['estado']}"
        assert diff["keys"]["regiao"] == "Sudeste"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
