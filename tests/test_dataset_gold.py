"""Tests for GOLD dataset validation and functionality."""

import pytest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.accuracy.processor import (
    compare_and_correct,
    read_dataset,
)


class TestGoldDatasetValidation:
    """Test GOLD dataset validation rules."""

    def setup_method(self):
        """Setup test data."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test data."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_gold_duplicate_keys_single_column(self):
        """Test that duplicate keys in GOLD dataset raise error with single key column."""
        gold_df = pd.DataFrame(
            {
                "id": ["A", "A", "B"],  # Duplicate A
                "value": [10.0, 15.0, 20.0],
            }
        )

        target_df = pd.DataFrame({"id": ["A", "B"], "value": [10.0, 20.0]})

        with pytest.raises(ValueError, match="Duplicate keys found in GOLD dataset"):
            compare_and_correct(
                gold_df,
                target_df,
                key_columns=["id"],
                value_columns=["value"],
                options={},
            )

    def test_gold_duplicate_keys_multiple_columns(self):
        """Test that duplicate composite keys in GOLD dataset raise error."""
        gold_df = pd.DataFrame(
            {
                "region": ["North", "North", "South"],
                "product": ["A", "A", "B"],  # Duplicate North+A
                "sales": [100.0, 150.0, 200.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "region": ["North", "South"],
                "product": ["A", "B"],
                "sales": [100.0, 200.0],
            }
        )

        with pytest.raises(ValueError, match="Duplicate keys found in GOLD dataset"):
            compare_and_correct(
                gold_df,
                target_df,
                key_columns=["region", "product"],
                value_columns=["sales"],
                options={},
            )

    def test_gold_no_duplicates_passes(self):
        """Test that GOLD dataset without duplicates passes validation."""
        gold_df = pd.DataFrame(
            {
                "id": ["A", "B", "C"],
                "value": [10.0, 20.0, 30.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "id": ["A", "B", "C"],
                "value": [10.0, 20.0, 30.0],
            }
        )

        # Should not raise error
        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["id"],
            value_columns=["value"],
            options={},
        )

        assert summary["rows_gold"] == 3
        assert summary["mismatches_total"] == 0

    def test_gold_duplicate_after_normalization(self):
        """Test that duplicates after key normalization are detected."""
        gold_df = pd.DataFrame(
            {
                "produto": ["Café", "CAFÉ", "Arroz"],  # Same after normalization
                "preco": [10.0, 15.0, 20.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "produto": ["Café", "Arroz"],
                "preco": [10.0, 20.0],
            }
        )

        # With normalization enabled (lowercase, strip accents)
        with pytest.raises(ValueError, match="Duplicate keys found in GOLD dataset"):
            compare_and_correct(
                gold_df,
                target_df,
                key_columns=["produto"],
                value_columns=["preco"],
                options={
                    "normalizeKeys": True,
                    "lowercase": True,
                    "stripAccents": True,
                },
            )

    def test_gold_duplicate_with_punctuation_normalization(self):
        """Test that duplicates after punctuation removal are detected."""
        gold_df = pd.DataFrame(
            {
                "code": ["A-123", "A123", "B-456"],  # Same after removing punctuation
                "value": [10.0, 15.0, 20.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "code": ["A-123", "B-456"],
                "value": [10.0, 20.0],
            }
        )

        with pytest.raises(ValueError, match="Duplicate keys found in GOLD dataset"):
            compare_and_correct(
                gold_df,
                target_df,
                key_columns=["code"],
                value_columns=["value"],
                options={
                    "normalizeKeys": True,
                    "stripPunctuation": True,
                },
            )

    def test_gold_column_validation(self):
        """Test that missing columns in GOLD dataset are detected."""
        gold_df = pd.DataFrame(
            {
                "id": ["A", "B"],
                "value": [10.0, 20.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "id": ["A", "B"],
                "value": [10.0, 20.0],
                "extra": [100, 200],
            }
        )

        # Try to use a column that doesn't exist in GOLD
        with pytest.raises(ValueError, match="Column 'nonexistent' not found in GOLD"):
            compare_and_correct(
                gold_df,
                target_df,
                key_columns=["id"],
                value_columns=["nonexistent"],
                options={},
            )


class TestGoldDatasetEdgeCases:
    """Test GOLD dataset edge cases."""

    def setup_method(self):
        """Setup test data."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test data."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_gold_empty_dataset(self):
        """Test handling of empty GOLD dataset."""
        gold_df = pd.DataFrame({"id": [], "value": []})
        target_df = pd.DataFrame({"id": ["A"], "value": [10.0]})

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["id"],
            value_columns=["value"],
            options={},
        )

        assert summary["rows_gold"] == 0
        assert summary["rows_target"] == 1
        assert summary["common_keys"] == 0

    def test_gold_single_row(self):
        """Test GOLD dataset with single row."""
        gold_df = pd.DataFrame({"id": ["A"], "value": [10.0]})
        target_df = pd.DataFrame({"id": ["A"], "value": [15.0]})

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["id"],
            value_columns=["value"],
            options={},
        )

        assert summary["rows_gold"] == 1
        assert summary["mismatches_total"] == 1
        assert len(differences) == 1

    def test_gold_with_nan_values(self):
        """Test GOLD dataset with NaN values in value columns."""
        gold_df = pd.DataFrame(
            {
                "id": ["A", "B", "C"],
                "value": [10.0, np.nan, 30.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "id": ["A", "B", "C"],
                "value": [10.0, 20.0, 30.0],
            }
        )

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["id"],
            value_columns=["value"],
            options={},
        )

        # NaN vs value should be detected as difference
        assert summary["mismatches_total"] == 1

    def test_gold_with_special_characters(self):
        """Test GOLD dataset with special characters in keys."""
        gold_df = pd.DataFrame(
            {
                "code": ["A@123", "B#456", "C$789"],
                "value": [10.0, 20.0, 30.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "code": ["A@123", "B#456", "C$789"],
                "value": [10.0, 20.0, 30.0],
            }
        )

        # Without normalization, should work
        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["code"],
            value_columns=["value"],
            options={"normalizeKeys": False},
        )

        assert summary["mismatches_total"] == 0

    def test_gold_numeric_keys(self):
        """Test GOLD dataset with numeric key columns."""
        gold_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "value": [10.0, 20.0, 30.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "value": [10.0, 25.0, 30.0],
            }
        )

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["id"],
            value_columns=["value"],
            options={},
        )

        assert summary["rows_gold"] == 3
        assert summary["mismatches_total"] == 1


class TestGoldDatasetAsReference:
    """Test GOLD dataset behavior as reference standard."""

    def setup_method(self):
        """Setup test data."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test data."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_gold_values_override_target(self):
        """Test that GOLD values override TARGET values in corrections."""
        gold_df = pd.DataFrame(
            {
                "produto": ["A", "B", "C"],
                "preco": [100.0, 200.0, 300.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "produto": ["A", "B", "C"],
                "preco": [111.0, 222.0, 333.0],  # All different
            }
        )

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["produto"],
            value_columns=["preco"],
            options={},
        )

        # All corrections should use GOLD values
        assert corrected_df["preco"].tolist() == [100.0, 200.0, 300.0]
        assert summary["mismatches_total"] == 3
        assert len(differences) == 3

    def test_gold_keys_define_expected_rows(self):
        """Test that GOLD dataset defines which rows should exist."""
        gold_df = pd.DataFrame(
            {
                "id": ["A", "B", "C"],
                "value": [10.0, 20.0, 30.0],
            }
        )

        # TARGET has extra row D
        target_df = pd.DataFrame(
            {
                "id": ["A", "B", "C", "D"],
                "value": [10.0, 20.0, 30.0, 40.0],
            }
        )

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["id"],
            value_columns=["value"],
            options={},
        )

        # Summary should report extra row in TARGET
        assert summary["extra_in_target"] == 1
        assert summary["common_keys"] == 3

    def test_gold_defines_missing_rows(self):
        """Test that GOLD dataset identifies missing rows in TARGET."""
        gold_df = pd.DataFrame(
            {
                "id": ["A", "B", "C"],
                "value": [10.0, 20.0, 30.0],
            }
        )

        # TARGET missing row C
        target_df = pd.DataFrame(
            {
                "id": ["A", "B"],
                "value": [10.0, 20.0],
            }
        )

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["id"],
            value_columns=["value"],
            options={},
        )

        # Summary should report missing row in TARGET
        assert summary["missing_in_target"] == 1
        assert summary["common_keys"] == 2

    def test_gold_multiple_value_columns(self):
        """Test GOLD dataset with multiple value columns to compare."""
        gold_df = pd.DataFrame(
            {
                "id": ["A", "B", "C"],
                "price": [10.0, 20.0, 30.0],
                "quantity": [100, 200, 300],
            }
        )

        target_df = pd.DataFrame(
            {
                "id": ["A", "B", "C"],
                "price": [10.0, 25.0, 30.0],  # B different
                "quantity": [100, 200, 350],  # C different
            }
        )

        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["id"],
            value_columns=["price", "quantity"],
            options={},
        )

        # Should have 2 mismatches (one in price, one in quantity)
        assert summary["mismatches_total"] == 2
        assert len(differences) == 2

        # Check both columns were corrected
        assert corrected_df[corrected_df["id"] == "B"]["price"].values[0] == 20.0
        assert corrected_df[corrected_df["id"] == "C"]["quantity"].values[0] == 300.0


class TestGoldDatasetFileOperations:
    """Test GOLD dataset file reading and validation."""

    def setup_method(self):
        """Setup test data."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test data."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_read_gold_csv_utf8(self):
        """Test reading GOLD dataset from UTF-8 CSV file."""
        gold_csv = Path(self.temp_dir) / "gold.csv"
        gold_df = pd.DataFrame(
            {
                "Produto": ["Café", "Açúcar", "Arroz"],
                "Preço": [10.50, 5.00, 8.75],
            }
        )
        gold_df.to_csv(gold_csv, index=False, encoding="utf-8")

        # Read it back
        loaded_df = read_dataset(gold_csv)

        assert len(loaded_df) == 3
        # Column names are not normalized by read_dataset - that happens in compare_and_correct
        assert "Produto" in loaded_df.columns
        assert "Preço" in loaded_df.columns
        # Verify data integrity
        assert loaded_df["Produto"].tolist() == ["Café", "Açúcar", "Arroz"]

    def test_gold_column_name_normalization(self):
        """Test that GOLD dataset column names are normalized."""
        gold_df = pd.DataFrame(
            {
                "Product ID": ["A", "B"],
                "Unit Price": [10.0, 20.0],
            }
        )

        target_df = pd.DataFrame(
            {
                "product_id": ["A", "B"],
                "unit_price": [10.0, 20.0],
            }
        )

        # Should work because columns are normalized
        corrected_df, summary, differences = compare_and_correct(
            gold_df,
            target_df,
            key_columns=["Product ID"],  # Will be normalized to product_id
            value_columns=["Unit Price"],  # Will be normalized to unit_price
            options={},
        )

        assert summary["mismatches_total"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
