"""
Quick validation script for synthetic dataset download fixes.

Run this to quickly verify the fixes are working:
    python tests/test_synthetic_download_quick.py
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from src.synthetic.routes import synth_bp
from src.synthetic.generator import SyntheticDataGenerator


def test_https_url_generation():
    """Quick test: HTTPS URL generation."""
    print("\n[1/5] Testing HTTPS URL generation...")

    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=0)
    app.register_blueprint(synth_bp)
    app.config["TESTING"] = True
    client = app.test_client()

    schema = {
        "columns": [
            {"name": "id", "type": "integer", "options": {"min": 1, "max": 100}}
        ]
    }

    response = client.post(
        "/api/synth/generate",
        data=json.dumps({"schema": schema, "rows": 5, "fileType": "csv"}),
        content_type="application/json",
        headers={
            "X-Forwarded-Proto": "https",
            "Host": "dataforgetest-backend.onrender.com",
        },
    )

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.get_json()
    download_url = data.get("downloadUrl", "")

    if not download_url.startswith("https://"):
        print(f"   ❌ FAIL: URL doesn't start with https:// : {download_url}")
        return False

    if "http://" in download_url:
        print(f"   ❌ FAIL: URL contains http:// (mixed content): {download_url}")
        return False

    print(f"   ✓ PASS: {download_url[:60]}...")
    return True


def test_csv_not_html():
    """Quick test: CSV download not HTML."""
    print("\n[2/5] Testing CSV download (not HTML)...")

    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=0)
    app.register_blueprint(synth_bp)
    app.config["TESTING"] = True
    client = app.test_client()

    schema = {
        "columns": [{"name": "id", "type": "integer", "options": {"min": 1, "max": 10}}]
    }

    # Generate
    response = client.post(
        "/api/synth/generate",
        data=json.dumps({"schema": schema, "rows": 3, "fileType": "csv"}),
        content_type="application/json",
    )

    if response.status_code != 200:
        print(f"   ❌ FAIL: Generation failed with status {response.status_code}")
        return False

    download_url = response.get_json()["downloadUrl"]

    # Extract path
    if download_url.startswith("http"):
        path = download_url.split("/api/synth/download/")[-1]
        download_path = f"/api/synth/download/{path}"
    else:
        download_path = download_url

    # Download
    dl_response = client.get(download_path)

    if dl_response.status_code != 200:
        print(f"   ❌ FAIL: Download failed with status {dl_response.status_code}")
        return False

    content = dl_response.data.decode("utf-8")

    # Check not HTML
    if content.strip().startswith(("<!DOCTYPE", "<html", "<HTML")):
        print(f"   ❌ FAIL: Content is HTML: {content[:100]}")
        return False

    # Check is CSV-like
    if "," not in content and "\n" not in content:
        print(f"   ❌ FAIL: Content doesn't look like CSV: {content[:100]}")
        return False

    print(f"   ✓ PASS: Downloaded {len(content)} bytes of CSV")
    return True


def test_model_provider_compatibility():
    """Quick test: Model/Provider compatibility."""
    print("\n[3/5] Testing model/provider compatibility...")

    # Should work: Gemini model with Gemini provider
    try:
        _ = SyntheticDataGenerator(
            api_key="test", model="gemini-2.0-flash-exp", provider="gemini"
        )
        print("   ✓ PASS: Gemini model + Gemini provider accepted")
    except ValueError as e:
        print(f"   ❌ FAIL: Gemini+Gemini should work: {e}")
        return False

    # Should fail: Claude model with Gemini provider
    # The generator logs the error but doesn't raise publicly (uses fallback)
    # Check that LLM is not available due to validation
    gen_invalid = SyntheticDataGenerator(
        api_key="test", model="claude-3-haiku-20240307", provider="gemini"
    )
    if gen_invalid._llm_available:
        print("   ❌ FAIL: Claude+Gemini should be rejected")
        return False
    print("   ✓ PASS: Claude model + Gemini provider correctly rejected")

    return True


def test_security_headers():
    """Quick test: Security headers present."""
    print("\n[4/5] Testing security headers...")

    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=0)
    app.register_blueprint(synth_bp)
    app.config["TESTING"] = True
    client = app.test_client()

    schema = {
        "columns": [{"name": "id", "type": "integer", "options": {"min": 1, "max": 5}}]
    }

    # Generate
    gen_resp = client.post(
        "/api/synth/generate",
        data=json.dumps({"schema": schema, "rows": 2, "fileType": "csv"}),
        content_type="application/json",
    )

    download_url = gen_resp.get_json()["downloadUrl"]

    if download_url.startswith("http"):
        path = download_url.split("/api/synth/download/")[-1]
        download_path = f"/api/synth/download/{path}"
    else:
        download_path = download_url

    # Download
    dl_resp = client.get(download_path)

    required_headers = [
        "Content-Type",
        "Content-Disposition",
        "X-Content-Type-Options",
        "Access-Control-Allow-Origin",
    ]

    missing = []
    for header in required_headers:
        if header not in dl_resp.headers:
            missing.append(header)

    if missing:
        print(f"   ❌ FAIL: Missing headers: {', '.join(missing)}")
        return False

    print(f"   ✓ PASS: All {len(required_headers)} security headers present")
    return True


def test_health_endpoint():
    """Quick test: Health endpoint exposes config."""
    print("\n[5/5] Testing health endpoint...")

    app = Flask(__name__)
    app.register_blueprint(synth_bp)
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/api/synth/health")

    if response.status_code != 200:
        print(f"   ❌ FAIL: Status {response.status_code}")
        return False

    data = response.get_json()

    required_keys = ["status", "provider", "model"]
    missing = [k for k in required_keys if k not in data]

    if missing:
        print(f"   ❌ FAIL: Missing keys: {', '.join(missing)}")
        return False

    print(f"   ✓ PASS: Provider={data['provider']}, Model={data['model']}")
    return True


def main():
    """Run all quick tests."""
    print("\n" + "=" * 70)
    print("QUICK VALIDATION: Synthetic Dataset Download Fixes")
    print("=" * 70)

    tests = [
        test_https_url_generation,
        test_csv_not_html,
        test_model_provider_compatibility,
        test_security_headers,
        test_health_endpoint,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ FAIL: Exception: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")

    if failed == 0:
        print("✓ ALL TESTS PASSED - Fixes are working correctly!")
    else:
        print(f"✗ {failed} test(s) failed - Review output above")

    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
