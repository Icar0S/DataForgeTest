"""Test full workflow: inspect -> DSL -> PySpark code generation."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dataset_inspector.inspector import inspect_dataset  # type: ignore
from dataset_inspector.dsl_generator import generate_dsl_from_metadata  # type: ignore
from code_generator.pyspark_generator import generate_pyspark_code  # type: ignore

# Test with the problematic CSV
csv_path = r"C:\Users\Icaro\Downloads\arrecadacao-estado.csv"

print("Testing FULL WORKFLOW with arrecadacao-estado.csv...")
print("=" * 80)

try:
    # Step 1: Inspect
    print("\n[STEP 1] Inspecting dataset...")
    metadata = inspect_dataset(csv_path, "csv", {})
    print("✓ Inspection successful!")
    print(f"  Encoding: {metadata['detected_options']['encoding']}")
    print(f"  Delimiter: '{metadata['detected_options']['delimiter']}'")
    print(f"  Rows: {metadata['row_count']}, Columns: {metadata['column_count']}")

    # Step 2: Generate DSL
    print("\n[STEP 2] Generating DSL...")
    dsl = generate_dsl_from_metadata(metadata, {})
    print("✓ DSL generation successful!")
    print(f"  Dataset name: {dsl.get('name', 'N/A')}")
    print(f"  Dataset section: {dsl.get('dataset', {}).get('name', 'N/A')}")
    print(f"  Schema fields: {len(dsl.get('schema', []))}")
    print(f"  Rules: {len(dsl.get('rules', []))}")

    # Show first few rules
    if dsl.get("rules"):
        print("\n  Sample rules:")
        for rule in dsl["rules"][:3]:
            print(f"    - {rule['type']}: {rule.get('column', 'N/A')}")

    # Step 3: Generate PySpark code
    print("\n[STEP 3] Generating PySpark code...")
    pyspark_code = generate_pyspark_code(dsl)
    print("✓ PySpark code generation successful!")
    print(f"  Code length: {len(pyspark_code)} characters")
    print(f"  Lines of code: {len(pyspark_code.splitlines())}")

    # Show first few lines
    print("\n  First 10 lines of generated code:")
    for i, line in enumerate(pyspark_code.splitlines()[:10], 1):
        print(f"    {i:2}. {line}")

    print("\n" + "=" * 80)
    print("✓✓✓ ALL STEPS COMPLETED SUCCESSFULLY! ✓✓✓")
    print("=" * 80)

except Exception as e:
    print("\n✗✗✗ ERROR OCCURRED ✗✗✗")
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")

    import traceback

    print("\nFull traceback:")
    traceback.print_exc()

    print("\n" + "=" * 80)
