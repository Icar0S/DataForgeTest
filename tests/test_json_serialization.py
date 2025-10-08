"""Test script to verify JSON serialization fixes for NaN values."""

import sys
import os
import numpy as np
import pandas as pd
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.metrics.routes import convert_to_json_serializable


def test_nan_inf_conversion():
    """Test conversion of NaN and inf values."""
    print("=== Testing NaN and Inf Conversion ===")

    test_cases = [
        ("NumPy NaN", np.nan),
        ("NumPy positive infinity", np.inf),
        ("NumPy negative infinity", -np.inf),
        ("Python float NaN", float("nan")),
        ("Python float inf", float("inf")),
        ("Python float -inf", float("-inf")),
        ("Normal float", 42.5),
        ("Normal int", 42),
        ("NumPy int64", np.int64(42)),
        ("NumPy float64", np.float64(42.5)),
        ("NumPy float64 NaN", np.float64("nan")),
    ]

    for name, value in test_cases:
        try:
            converted = convert_to_json_serializable(value)
            json_str = json.dumps(converted)
            print(f"✅ {name}: {value} -> {converted} -> JSON: {json_str}")
        except Exception as e:
            print(f"❌ {name}: {value} -> ERROR: {e}")


def test_complex_structure():
    """Test conversion of complex nested structures with NaN values."""
    print("\n=== Testing Complex Structures ===")

    # Create a structure similar to what metrics might return
    test_data = {
        "overall_quality_score": 85.5,
        "metrics": {
            "completeness": {
                "overall_completeness": 92.3,
                "column_completeness": {
                    "col1": {"completeness": 100.0, "missing_count": 0},
                    "col2": {
                        "completeness": np.nan,
                        "missing_count": 5,
                    },  # This could cause the error
                    "col3": {
                        "completeness": float("inf"),
                        "missing_count": np.inf,
                    },  # This too
                },
            },
            "uniqueness": {
                "overall_uniqueness": 78.9,
                "duplicate_rows": 15,
                "unique_values": [
                    1,
                    2,
                    np.nan,
                    4,
                    float("inf"),
                ],  # Array with problematic values
            },
        },
        "dataset_info": {
            "rows": 1000,
            "columns": 3,
            "memory_usage": np.float64(256.5),
        },
        "problematic_values": [np.nan, np.inf, -np.inf, 42.5, "normal_string"],
    }

    try:
        converted = convert_to_json_serializable(test_data)
        json_str = json.dumps(converted, indent=2)
        print("✅ Complex structure converted successfully:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)

        # Verify that the JSON can be parsed back
        parsed = json.loads(json_str)
        print("✅ JSON can be parsed back successfully")

        return converted

    except Exception as e:
        print(f"❌ Complex structure conversion failed: {e}")
        return None


def test_dataframe_metrics():
    """Test with actual DataFrame that might produce NaN values."""
    print("\n=== Testing Real DataFrame Metrics ===")

    # Create a DataFrame that might produce NaN in calculations
    df = pd.DataFrame(
        {
            "col1": [1, 2, None, 4, 5],
            "col2": ["a", "b", "c", None, "e"],
            "col3": [1.0, float("inf"), 3.0, 4.0, float("nan")],
            "col4": [None, None, None, None, None],  # All null column
        }
    )

    print(f"DataFrame shape: {df.shape}")
    print("DataFrame info:")
    print(df.describe())

    # Simulate some calculations that might produce NaN
    completeness_metrics = {}
    for col in df.columns:
        total_count = len(df)
        non_null_count = df[col].count()
        completeness = (
            (non_null_count / total_count * 100) if total_count > 0 else np.nan
        )

        completeness_metrics[col] = {
            "completeness": completeness,
            "missing_count": total_count - non_null_count,
            "non_null_count": non_null_count,
            "mean": df[col].mean() if df[col].dtype in ["int64", "float64"] else None,
            "std": df[col].std() if df[col].dtype in ["int64", "float64"] else None,
        }

    print("\nRaw completeness metrics:")
    for col, metrics in completeness_metrics.items():
        print(f"  {col}: {metrics}")

    try:
        converted = convert_to_json_serializable(completeness_metrics)
        json_str = json.dumps(converted, indent=2)
        print("\n✅ DataFrame metrics converted successfully:")
        print(json_str)

    except Exception as e:
        print(f"\n❌ DataFrame metrics conversion failed: {e}")


if __name__ == "__main__":
    print("Testing JSON Serialization for NaN/Inf Values")
    print("=" * 50)

    test_nan_inf_conversion()
    complex_result = test_complex_structure()
    test_dataframe_metrics()

    print("\n" + "=" * 50)
    print("Tests completed!")

    if complex_result:
        print(
            "\n🎉 All conversions successful! The JSON serialization issue should be resolved."
        )
    else:
        print("\n❌ Some conversions failed. The issue may persist.")
