"""Simulate HTTP requests to find JSON serialization issues."""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from dataset_inspector.inspector import inspect_dataset  # type: ignore
from dataset_inspector.dsl_generator import generate_dsl_from_metadata  # type: ignore
from code_generator.pyspark_generator import generate_pyspark_code  # type: ignore

test_files = [
    r"C:\Users\Icaro\Downloads\arrecadacao-estado.csv",
    r"C:\Users\Icaro\Downloads\ALUNOS-DA-GRADUACAO-2025-1.csv",
]


def check_json_serialization(obj, name):
    """Helper: verify an object can round-trip through JSON."""
    try:
        json_str = json.dumps(obj, ensure_ascii=False)
        print(f"  ✓ {name} serialization OK ({len(json_str)} chars)")

        # Try to deserialize
        json.loads(json_str)
        print(f"  ✓ {name} deserialization OK")
    except (TypeError, ValueError) as e:
        print(f"  ✗ {name} JSON error: {e}")


for csv_path in test_files:
    print("\n" + "=" * 80)
    print(f"Testing JSON serialization: {os.path.basename(csv_path)}")
    print("=" * 80)

    if not os.path.exists(csv_path):
        print(f"⚠ File not found: {csv_path}")
        continue

    try:
        # Step 1: Inspect
        print("\n[1] Inspect dataset...")
        metadata = inspect_dataset(csv_path, "csv", {})
        print(f"  Rows: {metadata['row_count']}, Columns: {metadata['column_count']}")

        # Test metadata JSON serialization
        print("\n[2] Testing metadata JSON serialization...")
        check_json_serialization(metadata, "Metadata")  # noqa

        # Step 2: Generate DSL
        print("\n[3] Generate DSL...")
        dsl = generate_dsl_from_metadata(metadata, {})

        # Test DSL JSON serialization
        print("\n[4] Testing DSL JSON serialization...")
        check_json_serialization(dsl, "DSL")  # noqa

        # Step 3: Generate PySpark code
        print("\n[5] Generate PySpark code...")
        pyspark_code = generate_pyspark_code(dsl)

        # Test response JSON serialization
        response = {
            "pyspark_code": pyspark_code,
            "filename": os.path.basename(csv_path).replace(".csv", "_validation.py"),
        }

        print("\n[6] Testing response JSON serialization...")
        check_json_serialization(response, "Response")  # noqa

        print(f"\n✓✓✓ ALL JSON TESTS PASSED for {os.path.basename(csv_path)} ✓✓✓")

    except Exception as e:
        print("\n✗✗✗ ERROR ✗✗✗")
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

print("\n" + "=" * 80)
print("JSON serialization testing complete!")
print("=" * 80)
