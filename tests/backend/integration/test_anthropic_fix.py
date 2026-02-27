"""Test suite for verifying the anthropic import fix and startup improvements."""

import sys
import os
import time
import subprocess
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))


def test_generator_import_without_anthropic():
    """Test that SyntheticDataGenerator can be imported even if anthropic fails."""
    print("\n=== Test 1: Import SyntheticDataGenerator ===")

    try:
        from src.synthetic.generator import SyntheticDataGenerator

        print("✓ SyntheticDataGenerator imported successfully")

        # Test initialization without API key
        gen = SyntheticDataGenerator(api_key="")
        print("✓ Generator initialized without API key")

        # Verify client is None when no API key
        assert gen.client is None, "Client should be None without API key"
        print("✓ Client is None as expected")

        return True
    except Exception as e:
        print(f"✗ Failed to import or initialize generator: {e}")
        return False


def test_api_import():
    """Test that the API can be imported without errors."""
    print("\n=== Test 2: Import Flask API ===")

    try:
        from src.api import app

        print("✓ Flask API imported successfully")
        print(f"✓ API has {len(app.blueprints)} blueprints registered")
        return True
    except Exception as e:
        print(f"✗ Failed to import API: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_backend_health_check():
    """Test backend health check endpoint."""
    print("\n=== Test 3: Backend Health Check ===")

    # Start backend in subprocess
    print("Starting Flask backend...")
    api_path = os.path.join(os.path.dirname(__file__), "..", "src", "api.py")

    process = subprocess.Popen(
        [sys.executable, api_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"),
    )

    # Wait for backend to start (max 30 seconds like in .bat files)
    print("Waiting for backend to be ready...")
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        time.sleep(1)
        try:
            response = requests.get("http://localhost:5000/", timeout=2)
            if response.status_code == 200:
                print(f"✓ Backend ready after {attempt} seconds")
                print(f"✓ Health check response: {response.json()}")

                # Test synthetic health endpoint
                synth_response = requests.get(
                    "http://localhost:5000/api/synth/health", timeout=2
                )
                if synth_response.status_code == 200:
                    print(f"✓ Synthetic service health check: {synth_response.json()}")

                # Clean up
                process.terminate()
                process.wait(timeout=5)
                return True
        except (requests.RequestException, requests.Timeout):
            print(f"  Waiting... {attempt}/{max_attempts}s")
            continue

    print(f"✗ Backend failed to respond within {max_attempts} seconds")
    process.terminate()
    process.wait(timeout=5)
    return False


def test_mock_data_generation():
    """Test that mock data generation works without anthropic."""
    print("\n=== Test 4: Mock Data Generation ===")

    try:
        from src.synthetic.generator import SyntheticDataGenerator

        gen = SyntheticDataGenerator(api_key="")  # No API key = mock mode

        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"unique": True}},
                {"name": "email", "type": "email", "options": {}},
            ]
        }

        records, logs = gen.generate_batch(schema, num_rows=5)

        print(f"✓ Generated {len(records)} mock records")
        print(f"✓ Logs: {logs}")

        # Verify we got records
        assert len(records) > 0, "Should generate at least some records"
        print(f"✓ Sample record: {records[0]}")

        # Verify the warning about mock data is in logs
        assert any(
            "mock data" in log.lower() for log in logs
        ), "Should log mock data usage"
        print("✓ Mock data mode properly logged")

        return True
    except Exception as e:
        print(f"✗ Failed to generate mock data: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing Anthropic Import Fix and Startup Improvements")
    print("=" * 70)

    results = {
        "Generator Import": test_generator_import_without_anthropic(),
        "API Import": test_api_import(),
        "Mock Data Generation": test_mock_data_generation(),
        "Backend Health Check": test_backend_health_check(),
    }

    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
