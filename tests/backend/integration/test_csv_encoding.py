"""Test script to diagnose CSV encoding issues with government data."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from dataset_inspector.inspector import inspect_dataset  # type: ignore

# Test with the problematic CSV
csv_path = r"C:\Users\Icaro\Downloads\arrecadacao-estado.csv"

print("Testing CSV inspection with arrecadacao-estado.csv...")
print("=" * 80)

try:
    # Test with auto-detection
    print("\n1. Testing with auto-detection:")
    metadata = inspect_dataset(csv_path, "csv", {})
    print(f"✓ Success! Detected encoding: {metadata['detected_options']['encoding']}")
    print(f"  Delimiter: '{metadata['detected_options']['delimiter']}'")
    print(f"  Rows: {metadata['row_count']}, Columns: {metadata['column_count']}")
    print("\n  First 3 columns:")
    for col in metadata["columns"][:3]:
        print(f"    - {col['name']} ({col['type']})")

except Exception as e:
    print(f"✗ Failed with auto-detection: {e}")
    print(f"  Error type: {type(e).__name__}")
    import traceback

    traceback.print_exc()

# Test with explicit encodings
encodings_to_test = ["utf-8", "latin-1", "iso-8859-1", "windows-1252", "cp1252"]

for encoding in encodings_to_test:
    print(f"\n2. Testing with explicit encoding: {encoding}")
    try:
        metadata = inspect_dataset(csv_path, "csv", {"encoding": encoding})
        print(f"✓ Success with {encoding}!")
        print(f"  Rows: {metadata['row_count']}, Columns: {metadata['column_count']}")
        print(
            f"  Sample column names: {[col['name'] for col in metadata['columns'][:3]]}"
        )
        break
    except Exception as e:
        print(f"✗ Failed with {encoding}: {e}")

print("\n" + "=" * 80)
print("Test complete!")
