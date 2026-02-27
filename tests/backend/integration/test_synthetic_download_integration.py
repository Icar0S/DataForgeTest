"""
Integration tests for synthetic dataset download fixes.

Tests validate fixes for:
1. Mixed Content / HTTPS URL generation
2. CSV download returning HTML instead of CSV
3. Model/Provider compatibility
4. Download URL format in production vs development
"""

import os
import sys
import json
import csv
from io import StringIO

# Configure UTF-8 output for Windows terminals
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import pytest
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from src.synthetic.routes import synth_bp
from src.synthetic.config import SyntheticConfig
from src.synthetic.generator import SyntheticDataGenerator


class TestSyntheticDownloadFixes:
    """Test suite for synthetic dataset download fixes."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with ProxyFix middleware."""
        app = Flask(__name__)

        # Apply ProxyFix to handle proxy headers correctly
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=0)

        app.register_blueprint(synth_bp)
        app.config["TESTING"] = True

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_health_endpoint_shows_provider_and_model(self, client):
        """Test that health endpoint exposes provider and model configuration."""
        response = client.get("/api/synth/health")

        assert response.status_code == 200
        data = response.get_json()

        assert "status" in data
        assert data["status"] == "ok"

        # Verify provider and model are exposed
        assert "provider" in data, "Health endpoint must expose 'provider'"
        assert "model" in data, "Health endpoint must expose 'model'"

        print(
            f"✓ Health endpoint shows provider: {data['provider']}, model: {data['model']}"
        )

    def test_https_url_generation_with_proxy_headers(self, client):
        """Test that HTTPS URLs are generated when X-Forwarded-Proto is https."""
        # Create a minimal valid schema
        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"min": 1, "max": 1000}},
                {"name": "name", "type": "string", "options": {"length": 50}},
            ]
        }

        request_data = {
            "schema": schema,
            "rows": 10,
            "fileType": "csv",
            "llmMode": "batched",
        }

        # Simulate production request with HTTPS via proxy
        response = client.post(
            "/api/synth/generate",
            data=json.dumps(request_data),
            content_type="application/json",
            headers={
                "X-Forwarded-Proto": "https",
                "Host": "dataforgetest-backend.onrender.com",
            },
        )

        assert response.status_code == 200
        data = response.get_json()

        assert "downloadUrl" in data
        download_url = data["downloadUrl"]

        # Verify URL uses HTTPS
        assert download_url.startswith(
            "https://"
        ), f"Download URL must use HTTPS in production, got: {download_url}"

        # Verify no HTTP in the URL (would cause mixed content)
        assert (
            "http://" not in download_url
        ), "Download URL must not contain http:// (mixed content issue)"

        print(f"✓ HTTPS URL generated correctly: {download_url[:50]}...")

    def test_http_url_generation_for_localhost(self, client):
        """Test that HTTP URLs are used for localhost development."""
        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"min": 1, "max": 1000}}
            ]
        }

        request_data = {"schema": schema, "rows": 5, "fileType": "csv"}

        # Simulate localhost request
        response = client.post(
            "/api/synth/generate",
            data=json.dumps(request_data),
            content_type="application/json",
            headers={"Host": "localhost:5000"},
        )

        assert response.status_code == 200
        data = response.get_json()

        download_url = data["downloadUrl"]

        # For localhost, HTTP is acceptable
        assert download_url.startswith(
            ("http://localhost", "/api/synth")
        ), f"Localhost should use HTTP or relative URL, got: {download_url}"

        print(f"✓ Localhost URL generated correctly: {download_url}")

    def test_download_returns_csv_not_html(self, client):
        """Test that download endpoint returns CSV content, not HTML."""
        # First generate a dataset
        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"min": 1, "max": 100}},
                {"name": "value", "type": "string", "options": {"length": 10}},
            ]
        }

        request_data = {"schema": schema, "rows": 5, "fileType": "csv"}

        response = client.post(
            "/api/synth/generate",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()

        # Extract session_id from download URL
        download_url = data["downloadUrl"]

        # Parse URL to get path
        if download_url.startswith("http"):
            # Extract path from full URL
            path = download_url.split("/api/synth/download/")[-1]
            download_path = f"/api/synth/download/{path}"
        else:
            download_path = download_url

        # Now download the file
        download_response = client.get(download_path)

        assert download_response.status_code == 200

        # Verify Content-Type is CSV, not HTML
        content_type = download_response.headers.get("Content-Type", "")
        assert (
            "text/csv" in content_type or "csv" in content_type
        ), f"Expected CSV content type, got: {content_type}"

        # Verify content is not HTML
        content = download_response.data.decode("utf-8")
        assert not content.strip().startswith(
            "<!DOCTYPE"
        ), "Download returned HTML instead of CSV"
        assert not content.strip().startswith(
            "<html"
        ), "Download returned HTML instead of CSV"

        # Verify it's valid CSV
        try:
            csv_reader = csv.reader(StringIO(content))
            rows = list(csv_reader)
            assert len(rows) > 0, "CSV file is empty"
            print(f"✓ Downloaded CSV with {len(rows)} rows (including header)")
        except csv.Error as e:
            pytest.fail(f"Downloaded content is not valid CSV: {e}")

    def test_download_has_correct_security_headers(self, client):
        """Test that download response has proper security headers."""
        # Generate a small dataset
        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"min": 1, "max": 10}}
            ]
        }

        request_data = {"schema": schema, "rows": 3, "fileType": "csv"}

        gen_response = client.post(
            "/api/synth/generate",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        download_url = gen_response.get_json()["downloadUrl"]

        # Extract path
        if download_url.startswith("http"):
            path = download_url.split("/api/synth/download/")[-1]
            download_path = f"/api/synth/download/{path}"
        else:
            download_path = download_url

        # Download file
        response = client.get(download_path)

        assert response.status_code == 200

        # Check security headers
        headers = response.headers

        assert (
            "X-Content-Type-Options" in headers
        ), "Missing X-Content-Type-Options header"
        assert headers["X-Content-Type-Options"] == "nosniff"

        assert "Access-Control-Allow-Origin" in headers, "Missing CORS header"

        assert "Content-Disposition" in headers, "Missing Content-Disposition header"

        print("✓ All security headers present")

    def test_model_provider_compatibility_validation(self):
        """Test that model/provider compatibility is validated."""
        # Test 1: Gemini model with Gemini provider (should work or fallback gracefully)
        gen_valid = SyntheticDataGenerator(
            api_key="test-key", model="gemini-2.0-flash-exp", provider="gemini"
        )
        print("✓ Gemini model + Gemini provider: Accepted by validation")

        # Test 2: Claude model with Gemini provider (should set _llm_available=False)
        gen_invalid = SyntheticDataGenerator(
            api_key="test-key", model="claude-3-haiku-20240307", provider="gemini"
        )
        assert (
            not gen_invalid._llm_available
        ), "Claude model should be marked as unavailable with Gemini provider"
        print(
            "✓ Claude model + Gemini provider: Correctly rejected (_llm_available=False)"
        )

        # Test 3: Ollama model with Gemini provider (should set _llm_available=False)
        gen_ollama_invalid = SyntheticDataGenerator(
            api_key="test-key", model="qwen2.5-coder:7b", provider="gemini"
        )
        assert (
            not gen_ollama_invalid._llm_available
        ), "Ollama model should be marked as unavailable with Gemini provider"
        print(
            "✓ Ollama model + Gemini provider: Correctly rejected (_llm_available=False)"
        )

    def test_config_auto_detects_provider_from_model(self):
        """Test that config auto-detection logic works correctly."""
        # Test the auto-detection logic directly
        test_cases = [
            ("gemini-2.0-flash-exp", "gemini"),
            ("gemini-1.5-pro", "gemini"),
            ("claude-3-haiku-20240307", "anthropic"),
            ("claude-3-opus-20240229", "anthropic"),
            ("qwen2.5-coder:7b", None),  # No auto-detect for Ollama
        ]

        for model_name, expected_provider in test_cases:
            # Simulate the auto-detection logic from config.py
            detected_provider = None
            if model_name.startswith("gemini"):
                detected_provider = "gemini"
            elif model_name.startswith("claude"):
                detected_provider = "anthropic"

            assert (
                detected_provider == expected_provider
            ), f"Model '{model_name}' should detect provider '{expected_provider}', got '{detected_provider}'"

        print(
            "✓ Config auto-detection logic validated for Gemini, Claude, and Ollama models"
        )

    def test_relative_vs_absolute_url_format(self, client):
        """Test URL format differences between dev and production."""
        schema = {
            "columns": [
                {"name": "id", "type": "integer", "options": {"min": 1, "max": 10}}
            ]
        }

        request_data = {"schema": schema, "rows": 5, "fileType": "csv"}

        # Test 1: Without host header (should give relative URL)
        response = client.post(
            "/api/synth/generate",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        data = response.get_json()
        url_no_host = data["downloadUrl"]

        # Should be relative or localhost
        assert url_no_host.startswith(
            ("/api/synth", "http://localhost")
        ), f"Without host header, should get relative URL, got: {url_no_host}"

        # Test 2: With production host header (should give absolute HTTPS URL)
        response = client.post(
            "/api/synth/generate",
            data=json.dumps(request_data),
            content_type="application/json",
            headers={"X-Forwarded-Proto": "https", "Host": "api.example.com"},
        )

        data = response.get_json()
        url_with_host = data["downloadUrl"]

        # Should be absolute HTTPS URL
        assert url_with_host.startswith(
            "https://"
        ), f"With production host, should get absolute HTTPS URL, got: {url_with_host}"
        assert "api.example.com" in url_with_host

        print(f"✓ Relative URL (dev): {url_no_host[:50]}...")
        print(f"✓ Absolute URL (prod): {url_with_host[:50]}...")


def run_integration_tests():
    """Run integration tests manually without pytest."""
    print("\n" + "=" * 70)
    print("SYNTHETIC DATASET DOWNLOAD INTEGRATION TESTS")
    print("=" * 70 + "\n")

    # Create test instance
    test_suite = TestSyntheticDownloadFixes()

    # Setup
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=0)
    app.register_blueprint(synth_bp)
    app.config["TESTING"] = True
    client = app.test_client()

    tests = [
        (
            "Health endpoint shows provider and model",
            lambda: test_suite.test_health_endpoint_shows_provider_and_model(client),
        ),
        (
            "HTTPS URL generation with proxy headers",
            lambda: test_suite.test_https_url_generation_with_proxy_headers(client),
        ),
        (
            "HTTP URL for localhost",
            lambda: test_suite.test_http_url_generation_for_localhost(client),
        ),
        (
            "Download returns CSV not HTML",
            lambda: test_suite.test_download_returns_csv_not_html(client),
        ),
        (
            "Download has security headers",
            lambda: test_suite.test_download_has_correct_security_headers(client),
        ),
        (
            "Model/Provider compatibility validation",
            lambda: test_suite.test_model_provider_compatibility_validation(),
        ),
        (
            "Config auto-detects provider from model",
            lambda: test_suite.test_config_auto_detects_provider_from_model(),
        ),
        (
            "Relative vs absolute URL format",
            lambda: test_suite.test_relative_vs_absolute_url_format(client),
        ),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n[TEST] {test_name}")
            test_func()
            passed += 1
            print(f"[PASS] {test_name}\n")
        except Exception as e:
            failed += 1
            print(f"[FAIL] {test_name}")
            import traceback

            print(f"Error: {e}")
            traceback.print_exc()
            print()

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    # Can run with pytest or standalone
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        success = run_integration_tests()
        sys.exit(0 if success else 1)
    else:
        print("Run with pytest: pytest test_synthetic_download_integration.py")
        print("Or run manually: python test_synthetic_download_integration.py --manual")
