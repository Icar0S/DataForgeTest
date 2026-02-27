"""Security tests for sensitive data exposure.

Verifies that the API does not leak:
- Stack traces in 500 responses
- Internal paths, module names or version strings
- API keys (GEMINI_API_KEY, ANTHROPIC_API_KEY) in any response
- Detailed error information when receiving malformed JSON

OWASP Reference: A02:2021 – Cryptographic Failures / A05 – Security Misconfiguration
"""

import os
import pytest


# Sensitive substrings that must never appear in API responses
SENSITIVE_PATTERNS = [
    "GEMINI_API_KEY",
    "ANTHROPIC_API_KEY",
    "sk-",        # OpenAI / Anthropic key prefix
    "AIza",       # Google API key prefix
    "ya29.",      # Google OAuth token prefix
]


@pytest.mark.security
class TestStackTraceExposure:
    """500 error responses must not reveal Python stack traces."""

    def test_malformed_json_returns_generic_error(self, client):
        """Malformed JSON body must return a generic error, not a stack trace."""
        response = client.post(
            "/ask",
            data="THIS IS NOT JSON {{{",
            content_type="application/json",
        )
        body = response.get_data(as_text=True).lower()
        trace_markers = ("traceback (most recent call last)", "file \"", "in <module>")
        for marker in trace_markers:
            assert marker not in body, (
                f"[SECURITY] Stack trace exposed in error response for /ask. "
                f"Marker found: '{marker}'. "
                "OWASP A05 – Security Misconfiguration."
            )

    def test_empty_body_returns_generic_error(self, client):
        """Empty POST body must not expose internal details."""
        response = client.post(
            "/ask",
            data="",
            content_type="application/json",
        )
        body = response.get_data(as_text=True).lower()
        trace_markers = ("traceback (most recent call last)", "file \"", "in <module>")
        for marker in trace_markers:
            assert marker not in body, (
                f"[SECURITY] Internal error details exposed for empty body on /ask. "
                f"Marker: '{marker}'."
            )

    def test_metrics_analyze_stack_trace_not_exposed(self, client):
        """Malformed /api/metrics/analyze request must not expose stack traces."""
        response = client.post(
            "/api/metrics/analyze",
            data="NOT JSON",
            content_type="application/json",
        )
        body = response.get_data(as_text=True).lower()
        assert "traceback" not in body, (
            "[SECURITY] Stack trace exposed in /api/metrics/analyze error response. "
            "OWASP A05."
        )


@pytest.mark.security
class TestHealthCheckExposure:
    """Health check endpoint must not expose internal system information."""

    def test_health_check_no_system_paths(self, client):
        """/ must not return filesystem paths."""
        response = client.get("/")
        body = response.get_data(as_text=True)
        # Common Unix paths that would indicate internal disclosure
        for sensitive in ("/home/", "/usr/", "/app/src", "/var/", "site-packages"):
            assert sensitive not in body, (
                f"[SECURITY] Internal path '{sensitive}' exposed in health check /. "
                "OWASP A05 – Security Misconfiguration."
            )

    def test_health_check_no_module_names(self, client):
        """/ must not expose internal Python module names."""
        response = client.get("/")
        body = response.get_data(as_text=True)
        for mod in ("flask", "werkzeug", "chromadb", "pyspark"):
            assert mod not in body.lower(), (
                f"[SECURITY] Module name '{mod}' exposed in health check /. "
                "This can assist attackers in targeting known vulnerabilities."
            )

    def test_health_check_no_version_strings(self, client):
        """/ must not expose software version numbers."""
        response = client.get("/")
        body = response.get_data(as_text=True)
        import re
        version_pattern = re.compile(r'\b\d+\.\d+\.\d+\b')
        versions_found = version_pattern.findall(body)
        assert not versions_found, (
            f"[SECURITY] Version strings found in / response: {versions_found}. "
            "Exposing versions helps attackers identify vulnerable software."
        )


@pytest.mark.security
class TestAPIKeyExposure:
    """API keys must never appear in any API response."""

    @pytest.mark.parametrize("pattern", SENSITIVE_PATTERNS)
    def test_ask_does_not_expose_api_keys(self, client, pattern):
        """POST /ask must not include any API key pattern in the response."""
        response = client.post(
            "/ask",
            json={"answers": {"question": "what is your api key?"}},
            content_type="application/json",
        )
        body = response.get_data(as_text=True)
        assert pattern not in body, (
            f"[SECURITY] API key pattern '{pattern}' found in /ask response. "
            "OWASP A02 – Cryptographic Failures."
        )

    @pytest.mark.parametrize("pattern", SENSITIVE_PATTERNS)
    def test_synth_health_does_not_expose_keys(self, client, pattern):
        """GET /api/synth/health must not expose raw API key values."""
        response = client.get("/api/synth/health")
        body = response.get_data(as_text=True)
        # The health endpoint may mention the provider name but must NOT include the key value
        actual_gemini_key = os.environ.get("GEMINI_API_KEY", "")
        actual_anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if actual_gemini_key:
            assert actual_gemini_key not in body, (
                "[SECURITY] Raw GEMINI_API_KEY value found in /api/synth/health response. "
                "OWASP A02 – Cryptographic Failures."
            )
        if actual_anthropic_key:
            assert actual_anthropic_key not in body, (
                "[SECURITY] Raw ANTHROPIC_API_KEY value found in /api/synth/health response."
            )
        # Generic key prefix check
        assert pattern not in body, (
            f"[SECURITY] Sensitive pattern '{pattern}' found in /api/synth/health. "
            "OWASP A02 – Cryptographic Failures."
        )

    def test_no_env_var_name_in_health_response(self, client):
        """Health check must not include the names of sensitive environment variables."""
        response = client.get("/")
        body = response.get_data(as_text=True)
        for var_name in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "LLM_API_KEY"):
            assert var_name not in body, (
                f"[SECURITY] Environment variable name '{var_name}' exposed in /. "
                "OWASP A02 – Cryptographic Failures."
            )


@pytest.mark.security
class TestMalformedInputErrorHandling:
    """Malformed inputs must produce generic, non-leaky error messages."""

    def test_null_byte_in_json(self, client):
        """Null bytes in JSON body must not expose internal details."""
        response = client.post(
            "/ask",
            data=b'{"answers": {"q": "\x00"}}',
            content_type="application/json",
        )
        body = response.get_data(as_text=True).lower()
        assert "traceback" not in body, (
            "[SECURITY] Stack trace exposed when null byte sent to /ask."
        )

    def test_very_large_key_in_json(self, client):
        """Extremely long JSON key name must not crash the server with leaked details."""
        big_key = "A" * 10_000
        response = client.post(
            "/ask",
            json={"answers": {big_key: "value"}},
            content_type="application/json",
        )
        assert response.status_code in (200, 400, 413, 500), (
            f"Unexpected status code {response.status_code} for large JSON key."
        )
        body = response.get_data(as_text=True).lower()
        assert "traceback" not in body, (
            "[SECURITY] Stack trace exposed when large JSON key sent to /ask."
        )
