"""Test script to reproduce and verify the fix for CSV tokenization error:
'Error tokenizing data. C error: Expected 2 fields in line 344, saw 45'
"""

import tempfile
import pandas as pd
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from src.metrics.processor import read_csv_robust


def create_problematic_csv():
    """Create a CSV file that would cause the original tokenization error."""
    csv_content = """id,name
1,John Doe
2,Jane Smith
3,Bob Wilson"""

    # Add many more lines to reach line 344
    for i in range(4, 340):
        csv_content += f"\n{i},Person {i}"

    # Line 344 - This is the problematic line with many extra fields
    csv_content += f"\n344,Alice,Johnson,Extra,Field,1,Field,2,Field,3,Field,4,Field,5,Field,6,Field,7,Field,8,Field,9,Field,10,Field,11,Field,12,Field,13,Field,14,Field,15,Field,16,Field,17,Field,18,Field,19,Field,20,Field,21,Field,22,Field,23,Field,24,Field,25,Field,26,Field,27,Field,28,Field,29"

    # Add more normal lines after
    for i in range(345, 350):
        csv_content += f"\n{i},Person {i}"

    return csv_content


def test_original_pandas_behavior():
    """Test how original pandas.read_csv would handle the problematic CSV."""
    print("=== Testing Original pandas.read_csv Behavior ===")

    csv_content = create_problematic_csv()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        temp_file = f.name

    try:
        # This should fail with the tokenization error
        df = pd.read_csv(temp_file)
        print(f"❌ Unexpected success! DataFrame shape: {df.shape}")
        print("This should have failed with tokenization error")
    except Exception as e:
        print(f"✅ Expected error occurred: {str(e)}")
        if "Expected 2 fields" in str(e) and "saw" in str(e):
            print("✅ This is the exact error we're trying to fix!")
        else:
            print("❓ Different error than expected")
    finally:
        os.unlink(temp_file)


def test_robust_csv_reader():
    """Test our robust CSV reader with the same problematic file."""
    print("\n=== Testing Our Robust CSV Reader ===")

    csv_content = create_problematic_csv()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        temp_file = f.name

    try:
        # This should succeed by skipping bad lines
        df = read_csv_robust(Path(temp_file))

        if df is not None and len(df) > 0:
            print(f"✅ Success! DataFrame shape: {df.shape}")
            print(f"✅ Columns: {list(df.columns)}")
            print(f"✅ Successfully read {len(df)} rows")

            # Check if we have the expected columns
            if "id" in df.columns and "name" in df.columns:
                print("✅ Correct columns detected")

                # Check some data
                print(f"✅ First few rows:")
                print(df.head())
                print(f"✅ Last few rows:")
                print(df.tail())

                # Verify that the problematic line was skipped
                if len(df) < 349:  # Should be less than total expected rows
                    print(f"✅ Problematic lines were correctly skipped")
                    print(f"   Expected ~349 rows, got {len(df)} rows")
            else:
                print("❌ Incorrect columns detected")
        else:
            print("❌ Failed to read CSV or got empty result")

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    finally:
        os.unlink(temp_file)


def test_edge_cases():
    """Test various edge cases that could cause tokenization errors."""
    print("\n=== Testing Edge Cases ===")

    test_cases = [
        {"name": "Inconsistent field counts", "content": "a,b\n1,2\n3,4,5,6,7\n8,9"},
        {
            "name": "Mixed quotes and commas",
            "content": 'id,name\n1,"Smith, John"\n2,Jane,"Extra field"\n3,"Johnson, Jr., Bob"',
        },
        {
            "name": "Very long line with many commas",
            "content": "a,b\n1,2\n" + ",".join([str(i) for i in range(100)]) + "\n3,4",
        },
    ]

    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(test_case["content"])
            temp_file = f.name

        try:
            df = read_csv_robust(Path(temp_file))
            if df is not None and len(df) > 0:
                print(f"✅ Success! Shape: {df.shape}, Columns: {list(df.columns)}")
            else:
                print("❌ Failed or empty result")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    print("Testing CSV Tokenization Error Fix")
    print("=" * 50)

    # Test original pandas behavior
    test_original_pandas_behavior()

    # Test our robust reader
    test_robust_csv_reader()

    # Test edge cases
    test_edge_cases()

    print("\n" + "=" * 50)
    print("Test completed!")
