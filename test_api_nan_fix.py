"""Test API endpoint with NaN handling."""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.api import app


def test_api_inspect_endpoint():
    """Test /api/datasets/inspect endpoint with NaN values."""
    print("🧪 Testing API endpoint with NaN handling...")

    # Create test client
    client = app.test_client()

    # Test file path
    csv_path = "test_nan_data.csv"

    if not os.path.exists(csv_path):
        print(f"❌ ERROR: Test file not found: {csv_path}")
        return False

    print(f"   Testing with: {csv_path}")

    try:
        # Upload file via API
        with open(csv_path, "rb") as f:
            response = client.post(
                "/api/datasets/inspect",
                data={
                    "file": (f, "test_nan_data.csv"),
                },
                content_type="multipart/form-data",
            )

        print(f"   Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ ERROR: Expected 200, got {response.status_code}")
            print(f"   Response: {response.get_data(as_text=True)}")
            return False

        # Get response data
        response_data = response.get_data(as_text=True)

        # Check for NaN in response (should not exist)
        if "NaN" in response_data:
            print("❌ ERROR: Found 'NaN' in API response (should be null)")
            print(f"   Response excerpt: {response_data[:500]}...")
            return False

        print("✅ No 'NaN' found in response (correct!)")

        # Parse as JSON to verify it's valid
        metadata = json.loads(response_data)

        print("✅ Response is valid JSON!")
        print(f"   Rows: {metadata.get('row_count')}")
        print(f"   Columns: {metadata.get('column_count')}")

        # Check preview
        if "preview" in metadata:
            print(f"   Preview rows: {len(metadata['preview'])}")
            # Check first row for null values
            if metadata["preview"]:
                first_row = metadata["preview"][0]
                null_fields = [k for k, v in first_row.items() if v is None]
                if null_fields:
                    print(f"   ✓ Null fields correctly represented: {null_fields}")

        # Check column stats
        if "columns" in metadata:
            for col in metadata["columns"]:
                if col["null_count"] > 0:
                    print(f"   ✓ Column '{col['name']}' has {col['null_count']} nulls")
                    # Check if any stats are None (which is OK)
                    if "min" in col and col["min"] is None:
                        print(
                            "(min/max are None, which is correct for all-null columns)"
                        )

        print("\n✅✅✅ API ENDPOINT TEST PASSED! ✅✅✅")
        print("The API correctly handles NaN values and returns valid JSON.")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON DECODE ERROR: {e}")
        print("The API response is not valid JSON")
        print(f"   Response: {response_data[:500]}...")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_api_inspect_endpoint()
    sys.exit(0 if success else 1)
