"""Test script to verify NaN handling in dataset inspector."""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.dataset_inspector.inspector import inspect_csv


def test_nan_handling():
    """Test that CSV with NaN values is properly serialized to JSON."""
    csv_path = "test_nan_data.csv"

    if not os.path.exists(csv_path):
        print(f"❌ ERROR: File not found: {csv_path}")
        print("Please ensure the CSV file is in the project root directory")
        return False

    print("🔍 Testing NaN handling in dataset inspector...")
    print(f"File: {csv_path}")

    try:
        # Inspect the CSV
        metadata = inspect_csv(csv_path)

        print("\n✓ CSV inspection successful!")
        print(f"   Rows: {metadata['row_count']}")
        print(f"   Columns: {metadata['column_count']}")
        print(f"   Encoding: {metadata['detected_options']['encoding']}")
        print(f"   Delimiter: {repr(metadata['detected_options']['delimiter'])}")

        # Try to serialize to JSON
        print("\n🔄 Attempting JSON serialization...")
        json_str = json.dumps(metadata, ensure_ascii=False)

        print("✅ JSON serialization successful!")
        print(f"   JSON length: {len(json_str)} characters")

        # Verify no NaN in the JSON string
        if "NaN" in json_str:
            print("❌ ERROR: Found 'NaN' in JSON output (should be null)")
            return False

        # Parse it back to verify it's valid JSON
        json.loads(json_str)
        print("✅ JSON is valid and can be parsed back!")

        # Check preview for any issues
        if "preview" in metadata:
            print(f"\n📋 Preview has {len(metadata['preview'])} rows")
            # Show first row keys
            if metadata["preview"]:
                print(f"   Columns in preview: {list(metadata['preview'][0].keys())}")

        # Check columns stats
        print("\n📊 Column statistics:")
        for col in metadata["columns"][:5]:  # Show first 5 columns
            print(
                f"   - {col['name']}: type={col['type']}, null_count={col['null_count']}"
            )
            if "min" in col:
                print(f"     Range: [{col['min']}, {col['max']}]")

        print("\n✅✅✅ ALL TESTS PASSED! ✅✅✅")
        print("The CSV with NaN values is now properly handled for JSON serialization.")
        return True

    except json.JSONDecodeError as e:
        print(f"\n❌ JSON ERROR: {e}")
        print("The metadata contains values that cannot be serialized to JSON")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_nan_handling()
    sys.exit(0 if success else 1)
