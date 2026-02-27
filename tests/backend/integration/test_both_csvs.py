"""Test both CSVs to find the production error."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from dataset_inspector.inspector import inspect_dataset  # type: ignore
from dataset_inspector.dsl_generator import generate_dsl_from_metadata  # type: ignore
from code_generator.pyspark_generator import generate_pyspark_code  # type: ignore

test_files = [
    r"C:\Users\Icaro\Downloads\arrecadacao-estado.csv",
    r"C:\Users\Icaro\Downloads\ALUNOS-DA-GRADUACAO-2025-1.csv",
]

for csv_path in test_files:
    print("\n" + "=" * 80)
    print(f"Testing: {os.path.basename(csv_path)}")
    print("=" * 80)

    if not os.path.exists(csv_path):
        print(f"⚠ File not found: {csv_path}")
        continue

    try:
        # Step 1: Inspect
        print("\n[1] Inspecting...")
        metadata = inspect_dataset(csv_path, "csv", {})
        print(f"✓ Rows: {metadata['row_count']}, Columns: {metadata['column_count']}")

        # Step 2: Generate DSL
        print("\n[2] Generating DSL...")
        dsl = generate_dsl_from_metadata(metadata, {})
        print(f"✓ Rules: {len(dsl.get('rules', []))}")

        # Step 3: Generate PySpark code
        print("\n[3] Generating PySpark code...")
        pyspark_code = generate_pyspark_code(dsl)
        print(
            f"✓ Code: {len(pyspark_code)} chars, {len(pyspark_code.splitlines())} lines"
        )

        print(f"\n✓✓✓ SUCCESS for {os.path.basename(csv_path)} ✓✓✓")

    except Exception as e:
        print(f"\n✗✗✗ ERROR for {os.path.basename(csv_path)} ✗✗✗")
        print(f"Error: {e}")
        print(f"Type: {type(e).__name__}")

        import traceback

        print("\nFull traceback:")
        traceback.print_exc()

print("\n" + "=" * 80)
print("Testing complete!")
print("=" * 80)
