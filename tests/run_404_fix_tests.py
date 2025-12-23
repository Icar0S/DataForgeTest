"""Run all integration tests for the 404 fix.

This script runs all tests related to the blueprint registration fix.

Usage:
    python tests/run_404_fix_tests.py

Or with pytest:
    pytest tests/test_blueprint_registration.py -v
    pytest tests/test_metrics_e2e_integration.py -v
    pytest tests/test_registration_resilience.py -v
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def run_test_file(test_file, description):
    """Run a specific test file and report results."""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "-s"],
        cwd=Path(__file__).parent.parent,
        capture_output=False,
    )

    return result.returncode == 0


def main():
    """Run all 404 fix related tests."""
    print("\n" + "=" * 80)
    print("INTEGRATION TESTS FOR BLUEPRINT REGISTRATION FIX")
    print("Issue: 404 error on /api/metrics/analyze")
    print("Date: December 23, 2025")
    print("=" * 80)

    test_files = [
        ("tests/test_blueprint_registration.py", "Blueprint Registration System Tests"),
        (
            "tests/test_metrics_e2e_integration.py",
            "Metrics End-to-End Integration Tests",
        ),
        ("tests/test_registration_resilience.py", "Registration Resilience Tests"),
    ]

    results = {}

    for test_file, description in test_files:
        test_path = Path(__file__).parent.parent / test_file

        if not test_path.exists():
            print(f"\n⚠️  Test file not found: {test_file}")
            results[description] = False
            continue

        success = run_test_file(str(test_path), description)
        results[description] = success

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    all_passed = True
    for description, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status:12} - {description}")
        if not success:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n✓ ALL TESTS PASSED!")
        print("The blueprint registration fix is working correctly.")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("Please review the failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
